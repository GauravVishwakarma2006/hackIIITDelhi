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

from app.matcher.ranking import (
    rank_caregivers,
    haversine_distance,
    load_caregivers,
    calculate_language_score,
    calculate_skill_score
)

__all__ = [
    "rank_caregivers",
    "haversine_distance",
    "load_caregivers",
    "calculate_language_score",
    "calculate_skill_score"
]
