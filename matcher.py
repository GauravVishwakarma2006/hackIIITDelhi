"""
matcher.py - Multi-Criteria Caregiver Matcher (Hack IIITD CAI).
Discards 8 inactive caregivers (filters 60 down to 52 active candidates).
Computes official rubric formula:
Score = 0.35 * Language + 0.30 * Proximity + 0.20 * Skill + 0.15 * Rating
Outputs top 1 to 3 caregivers with explicit plain-language explainability strings.
Emergency path returns empty list [].
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas import Location
from app.matcher.ranking import (
    rank_caregivers as _orig_rank_caregivers,
    haversine_distance,
    load_caregivers,
    calculate_language_score,
    calculate_skill_score
)


def rank_caregivers(*args, **kwargs):
    """
    Flexible interface supporting both:
    1. rank_caregivers(csv_path, care_type, lat, lng, top_k=3) -> returns list of dicts with 'caregiver_id'
    2. rank_caregivers(care_type, Location(lat, lng), detected_language, top_k) -> returns List[MatchedCaregiver]
    """
    if len(args) >= 4 and isinstance(args[0], str) and (args[0].endswith(".csv") or args[0].endswith(".json")):
        csv_path, care_type, lat, lng = args[:4]
        top_k = kwargs.get("top_k", args[4] if len(args) > 4 else 3)
        loc = Location(lat=float(lat), lng=float(lng))
        raw_matches = _orig_rank_caregivers(care_type=care_type, patient_loc=loc, top_k=top_k)
        return [
            {
                "caregiver_id": m.caregiver_id,
                "score": m.score,
                "reason": m.reason,
                "name": m.name,
                "role": m.role,
                "distance_km": m.distance_km,
                "available_slot": m.available_slot,
                "rating": m.rating
            }
            for m in raw_matches
        ]
    return _orig_rank_caregivers(*args, **kwargs)


__all__ = [
    "rank_caregivers",
    "haversine_distance",
    "load_caregivers",
    "calculate_language_score",
    "calculate_skill_score"
]
