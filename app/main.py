"""
CareCompass REST API Server.
Conforms strictly to the Hack IIITD (CAI, IIIT-Delhi) API contract.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import TriageRequest, TriageResponse
from app.engine.red_flags import detect_red_flags, get_emergency_protocol
from app.engine.intake import extract_symptoms, determine_follow_up
from app.engine.triage import classify_triage
from app.matcher.ranking import rank_caregivers

app = FastAPI(
    title="CareCompass API",
    description="AI-powered care navigation and safety-first caregiver matching (Hack IIITD - CAI)",
    version="1.0.0"
)

# Enable CORS for frontend and external evaluators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareCompass",
        "organization": "CAI, IIIT-Delhi Hackathon",
        "version": "1.0.0"
    }


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
        emergency_reason = get_emergency_protocol(red_flags, request.language or "hi")
        return TriageResponse(
            follow_up_question=None,
            care_type="emergency",
            urgency="immediate",
            red_flags=list(set(red_flags)),
            reasoning=emergency_reason,
            matched_caregivers=[]
        )

    # Step 2: Multilingual Symptom Extraction
    extracted = extract_symptoms(user_text)

    # Step 3: Check if targeted clinical follow-up is needed
    follow_up = determine_follow_up(user_text, request.conversation_history, extracted)
    if follow_up:
        return TriageResponse(
            follow_up_question=follow_up,
            care_type=None,
            urgency=None,
            red_flags=[],
            reasoning="Targeted clinical inquiry required to rule out acute severity or clarify treatment need.",
            matched_caregivers=[]
        )

    # Step 4: Final Clinical Triage Classification
    care_type, urgency, reasoning = classify_triage(extracted, is_emergency=False, red_flags=[])

    # Step 5: Multi-Criteria Caregiver Matching
    loc = request.location
    matched = rank_caregivers(
        care_type=care_type,
        patient_loc=loc,
        patient_lang=request.language or "Hindi",
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
