"""
triage_classifier.py - Routine Care Classification Engine (Hack IIITD CAI).
Conforms strictly to evaluate.py benchmark expectations.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engine.triage import classify_routine_care, classify_triage

__all__ = ["classify_routine_care", "classify_triage"]
