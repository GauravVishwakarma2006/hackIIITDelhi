"""
tinyfish_agent.py - Live Hospital Lookup Web Agent (Hack IIITD CAI).
Created by Shiv Chopra (Ignite Room / TinyFish Ambassador, IIIT-Delhi).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tinyfish_agent import (
    fetch_live_emergency_contacts,
    fetch_live_emergency_facilities,
    VERIFIED_DELHI_TRAUMA_CENTERS
)

__all__ = [
    "fetch_live_emergency_contacts",
    "fetch_live_emergency_facilities",
    "VERIFIED_DELHI_TRAUMA_CENTERS"
]
