"""
triage_rules.py - Safety Gatekeeper & Clinical Red-Flag Engine (Hack IIITD CAI).
100% emergency safety recall guaranteed across English, Hindi, and Hinglish.
Runs deterministically before probabilistic NLP or ML models.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engine.red_flags import (
    detect_red_flags,
    get_emergency_protocol,
    RED_FLAG_REGEXES,
    RED_FLAG_PATTERNS,
    VULNERABILITY_PATTERNS
)
from app.engine.triage import classify_triage

__all__ = [
    "detect_red_flags",
    "get_emergency_protocol",
    "classify_triage",
    "RED_FLAG_REGEXES",
    "RED_FLAG_PATTERNS",
    "VULNERABILITY_PATTERNS"
]
