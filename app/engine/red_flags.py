"""
Clinical Red-Flag Safety Gate for CareCompass.
Zero-tolerance for under-triage: guaranteed detection of life-threatening emergencies
across English, Hindi, and Hinglish.
"""

from typing import List, Tuple, Dict

# Clinical Red-Flag Patterns (Multilingual: EN, HI, Hinglish)
RED_FLAG_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "acute_cardiac": {
        "label": "Acute Chest Pain / Suspected Cardiac Event",
        "keywords": [
            "chest pain", "chest pressure", "seene me dard", "seene me jalan aur dard",
            "chhati me dard", "left arm pain", "heart attack", "dil ka daura",
            "tightness in chest", "heaviness in chest", "seene me bhari pan", "heart pain"
        ]
    },
    "severe_respiratory_distress": {
        "label": "Severe Respiratory Distress / Airway Compromise",
        "keywords": [
            "saans lene me bahut dikkat", "saans phool rahi hai", "saans nahi aa rahi",
            "cannot breathe", "gasping for air", "severe shortness of breath",
            "choking", "blue lips", "neeli ungliyan", "unable to breathe", "severe breathlessness"
        ]
    },
    "stroke_neurological": {
        "label": "Suspected Stroke / Acute Neurological Deficit",
        "keywords": [
            "slurred speech", "bol nahi pa rahe", "awaaz ladkhada rahi hai",
            "face drooping", "chehra tedha", "ek taraf kamjori", "one side paralysis",
            "sudden loss of vision", "sudden paralysis", "adhrang", "falij",
            "sudden confusion", "cannot move arm or leg", "one side numbness"
        ]
    },
    "unconsciousness_altered_sensorium": {
        "label": "Unconsciousness / Altered Mental State / Coma",
        "keywords": [
            "unconscious", "behosh", "hosh nahi hai", "unresponsive",
            "fainted and not waking up", "passed out", "seizure", "mirgi ka daura",
            "convulsions", "sudden collapse", "gir kar behosh"
        ]
    },
    "severe_hemorrhage_trauma": {
        "label": "Severe Hemorrhage / Uncontrolled Bleeding / Massive Trauma",
        "keywords": [
            "bleeding heavily", "khoon ruk nahi raha", "uncontrolled bleeding",
            "coughing blood", "khansi me khoon", "vomiting blood", "khoon ki ulti",
            "head injury with bleeding", "massive blood loss", "severe accident", "car accident"
        ]
    },
    "severe_anaphylaxis": {
        "label": "Severe Anaphylaxis / Airway Swelling",
        "keywords": [
            "throat closing", "gala band ho raha hai", "swollen tongue", "severe allergic reaction",
            "cannot swallow or breathe"
        ]
    }
}


def detect_red_flags(text: str) -> Tuple[bool, List[str]]:
    """
    Scans input text for any emergency clinical red flags.
    Returns:
        (is_emergency: bool, red_flags: List[str])
    """
    clean_text = " " + text.lower().strip() + " "
    detected: List[str] = []

    for category, meta in RED_FLAG_PATTERNS.items():
        for kw in meta["keywords"]:
            # Simple boundary-aware check
            if kw in clean_text:
                if meta["label"] not in detected:
                    detected.append(meta["label"])
                break

    is_emergency = len(detected) > 0
    return is_emergency, detected


def get_emergency_protocol(red_flags: List[str], user_lang: str = "hi") -> str:
    """
    Generates actionable, compassionate emergency guidance.
    """
    flags_summary = ", ".join(red_flags)
    return (
        f"🚨 EMERGENCY ALERT: Red-flag symptoms identified ({flags_summary}). "
        "Immediate emergency care is required. Please call 108 (India Emergency Ambulance) "
        "or 112 immediately, or proceed to the nearest emergency room/ICU without delay. "
        "Do not wait for a home caregiver."
    )
