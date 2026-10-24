"""
CareCompass REST API Server.
Conforms strictly to the Hack IIITD (CAI, IIIT-Delhi) API contract and evaluation taxonomy.
"""

import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import TriageRequest, TriageResponse
from app.engine.red_flags import detect_red_flags, get_emergency_protocol
from app.engine.intake import determine_follow_up
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

    # Step 2: Check if targeted clinical follow-up is needed (underspecified queries)
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

    # Step 3: Final Clinical Triage Classification
    # Concatenate prior user turns with user_input so follow-up turns retain full clinical context
    full_context = user_text
    if request.conversation_history:
        past_turns = " ".join([t.content for t in request.conversation_history if t.role == "user" and t.content.strip()])
        if past_turns:
            full_context = f"{past_turns} {user_text}"

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
