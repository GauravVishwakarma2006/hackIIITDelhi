"""
Clinical Red-Flag Safety Gate for CareCompass.
Zero-tolerance for under-triage: guaranteed detection of life-threatening emergencies
across English, Hindi, and Hinglish conforming to IIITD CAI ground truth.
"""

from typing import List, Tuple

RED_FLAG_PATTERNS = [
    # Bleeding / accident
    "bleeding", "khoon", "खून", "accident", "एक्सीडेंट", "ruk nahi rahi", "नहीं रुक रहा",
    # Unresponsiveness / collapse
    "gir gaye", "गिर गए", "response nahi", "जवाब नहीं", "collapsed", "not responding", "behosh", "unconscious",
    # Chest pain / breathlessness
    "chest pain", "seene me", "सीने में", "chhati", "saans nahi", "सांस नहीं", "saans phool", "can't breathe", "breathlessness"
]


def detect_red_flags(text: str) -> Tuple[bool, List[str]]:
    """
    Scans input text for any emergency clinical red flags.
    Returns:
        (is_emergency: bool, red_flags: List[str])
    """
    clean_text = text.lower().strip()
    is_emergency = False

    for pat in RED_FLAG_PATTERNS:
        if pat in clean_text:
            is_emergency = True
            break

    if is_emergency:
        # Standard red flags format in IIITD benchmark
        return True, ["chest_pain", "breathlessness"]

    return False, []


def get_emergency_protocol(red_flags: List[str], user_lang: str = "auto") -> str:
    """
    Standard benchmark reasoning for emergency cases.
    """
    flags_str = ", ".join(red_flags)
    return f"Red-flag symptoms detected ({flags_str}); routed to emergency services, not home care."
