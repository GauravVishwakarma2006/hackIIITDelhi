"""
Root app.py entry point for Hack IIITD (CAI, IIIT-Delhi) Automated Scorer.
Conforms strictly to the official benchmark runner contract:
- Exposes FastAPI app object with POST /triage and POST /api/v1/triage
- Run directly via: python app.py or uvicorn app:app
"""

import os
import sys

# Crucial: Allow app.py to act as both root module and package for submodules
__path__ = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")]

from app.main import app, triage_endpoint, health_check
from app.schemas import TriageRequest, TriageResponse, CareType, UrgencyLevel, MatchedCaregiver

__all__ = ["app", "triage_endpoint", "health_check", "TriageRequest", "TriageResponse", "CareType", "UrgencyLevel", "MatchedCaregiver"]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
