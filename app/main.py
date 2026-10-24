"""
CareCompass REST API Server.
Conforms strictly to the Hack IIITD (CAI, IIIT-Delhi) API contract and evaluation taxonomy.
"""

import os
import re
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import TriageRequest, TriageResponse, Location
from app.engine.red_flags import detect_red_flags, get_emergency_protocol, check_observer_alert
from app.engine.intake import determine_follow_up
from app.engine.domain_guard import check_health_domain
from app.engine.triage import classify_triage
from app.matcher.ranking import rank_caregivers

from app.tinyfish_agent import fetch_live_emergency_facilities

app = FastAPI(
    title="CareCompass API",
    description="AI-powered care navigation and safety-first caregiver matching (Hack IIITD - CAI)",
    version="1.0.0"
)

# Enable CORS for frontend and automated evaluators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Sub-50ms Response Latency Proof:
    Attaches X-Process-Time execution timer header in milliseconds.
    """
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


def detect_language(text: str) -> str:
    """Detects whether input is Hindi (Devanagari), Hinglish, or English."""
    if re.search(r'[\u0900-\u097F]', text):
        return "Hindi"
    # Basic Hinglish word heuristics
    hinglish_markers = ["papa", "mummy", "dadi", "dadaji", "hai", "nahi", "ruk", "ghav", "chahiye", "karwana", "lagwana", "bhi", "ko"]
    lower = text.lower()
    if any(m in lower.split() for m in hinglish_markers):
        return "Hinglish"
    return "English"


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareCompass",
        "organization": "CAI, IIIT-Delhi Hackathon",
        "version": "1.0.0"
    }


@app.get("/emergency/facilities")
@app.get("/api/v1/emergency/facilities")
async def emergency_facilities(lat: float = 28.5445, lng: float = 77.2725):
    """
    Decoupled live emergency directory. Returns verified 24x7 trauma centers
    without blocking triage execution.
    """
    facilities = await fetch_live_emergency_facilities(Location(lat=lat, lng=lng))
    return {"facilities": facilities}


@app.get("/emergency/live-contacts")
@app.get("/api/v1/emergency/live-contacts")
def emergency_live_contacts(area: str = "South Delhi"):
    """
    TinyFish Autonomous Web Agent (Shiv Chopra / Ignite Room / TinyFish Ambassador, IIIT-Delhi).
    Extracts live government hospital emergency desk phone and ICU status.
    """
    from app.tinyfish_agent import fetch_live_emergency_contacts
    return fetch_live_emergency_contacts(area=area)


@app.post("/triage", response_model=TriageResponse)
@app.post("/api/v1/triage", response_model=TriageResponse)
def triage_endpoint(request: TriageRequest) -> TriageResponse:
    """
    Main Triage API conforming strictly to IIITD CAI challenge specification.
    Inputs: user_input, language, location, conversation_history
    Outputs: follow_up_question OR (care_type, urgency, red_flags, reasoning, matched_caregivers)
    """
    user_text = request.user_input.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="user_input cannot be empty")

    detected_lang = detect_language(user_text)
    if request.language and request.language.lower() != "auto":
        detected_lang = request.language

    # Step 1: Zero-tolerance Clinical Red-Flag Safety Gate
    is_emergency, red_flags = detect_red_flags(user_text)

    # Also inspect prior conversation turns for emerging red flags
    if not is_emergency and request.conversation_history:
        for turn in request.conversation_history:
            if turn.role == "user":
                em_check, flags_check = detect_red_flags(turn.content)
                if em_check:
                    is_emergency = True
                    red_flags.extend(flags_check)

    if is_emergency:
        # Emergency path skips follow-ups and matching directly
        emergency_reason = get_emergency_protocol(red_flags, detected_lang)
        return TriageResponse(
            follow_up_question=None,
            care_type="emergency_112",
            urgency="emergency",
            red_flags=list(set(red_flags)),
            reasoning=emergency_reason,
            matched_caregivers=[]
        )

    # Step 1B: Clinical Domain Guard (Reject non-health queries like math, quadratic equation, code, trivia)
    is_health, non_health_msg = check_health_domain(user_text, detected_lang)
    if not is_health:
        return TriageResponse(
            follow_up_question=non_health_msg,
            care_type=None,
            urgency=None,
            red_flags=[],
            reasoning="Invalid input: Non-health query detected — CareCompass strictly handles healthcare symptoms and care navigation.",
            matched_caregivers=[]
        )

    # Step 2: Observer / Guard Mode Alert (Padosi / Guard third-party distress)
    is_observer, obs_reason = check_observer_alert(user_text)
    if is_observer:
        return TriageResponse(
            follow_up_question=None,
            care_type="paramedic_home_visit",
            urgency="emergency",
            red_flags=["observer_welfare_alert"],
            reasoning=obs_reason,
            matched_caregivers=[]
        )

    # Step 3: Check if targeted clinical follow-up is needed (underspecified queries)
    follow_up = determine_follow_up(user_text, request.conversation_history)
    if follow_up:
        return TriageResponse(
            follow_up_question=follow_up,
            care_type=None,
            urgency=None,
            red_flags=[],
            reasoning="Intent underspecified — asking a follow-up before deciding care type.",
            matched_caregivers=[]
        )

    # Step 4: Final Clinical Triage Classification
    # Concatenate prior user turns with user_input so follow-up turns retain full clinical context
    full_context = user_text
    if request.conversation_history:
        past_turns = " ".join([t.content for t in request.conversation_history if t.role == "user" and t.content.strip()])
        if past_turns:
            full_context = f"{past_turns} {user_text}"

    # Also double check domain on full_context
    is_health_full, non_health_msg_full = check_health_domain(full_context, detected_lang)
    if not is_health_full:
        return TriageResponse(
            follow_up_question=non_health_msg_full,
            care_type=None,
            urgency=None,
            red_flags=[],
            reasoning="Invalid input: Non-health query detected — CareCompass strictly handles healthcare symptoms and care navigation.",
            matched_caregivers=[]
        )

    care_type, urgency, reasoning = classify_triage(full_context, is_emergency=False, red_flags=[])

    # Step 4: Multi-Criteria Caregiver Matching
    loc = request.location
    matched = rank_caregivers(
        care_type=care_type,
        patient_loc=loc,
        detected_language=detected_lang,
        top_k=3
    )

    return TriageResponse(
        follow_up_question=None,
        care_type=care_type,
        urgency=urgency,
        red_flags=[],
        reasoning=reasoning,
        matched_caregivers=matched
    )


# Serve Static UI Frontend
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def serve_ui():
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "CareCompass API active. Visit /docs for documentation."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
