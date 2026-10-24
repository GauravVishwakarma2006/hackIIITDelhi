"""
Module 1: Smart Intake & Dialogue Manager.
Parses multilingual symptoms (English, Hindi, Hinglish), tracks conversational history,
and asks targeted, clinical follow-up questions when necessary.
"""

import re
from typing import Dict, List, Optional, Any
from app.schemas import ConversationTurn

# Multilingual Symptom Dictionary
SYMPTOM_LEXICON = {
    "fever": ["fever", "bukhar", "taap", "temperature", "garam sar"],
    "cough": ["cough", "khansi", "balgam", "dry cough", "sukhi khansi"],
    "respiratory": ["saans", "breath", "wheezing", "asthma", "dam foolna"],
    "chest_pain": ["chest pain", "seene me dard", "chhati me dard", "heart pain"],
    "wound": ["wound", "cut", "ghav", "chot", "patti", "bandage", "dressing", "stitches", "tanke"],
    "injection_iv": ["injection", "teeka", "iv", "drip", "glucose chadhana", "catheter", "nalli"],
    "elderly": ["papa", "mummy", "dada", "dadi", "nana", "nani", "elderly", "buzurg", "budhe", "old age", "father", "mother"],
    "child": ["bachha", "baby", "kid", "child", "beta", "beti", "infant"],
    "stomach": ["pet dard", "stomach pain", "loose motion", "dast", "ulti", "vomiting", "gas"],
    "joint_ortho": ["joint pain", "ghutne me dard", "kamar dard", "back pain", "fracture", "haddi me dard"],
    "chronic": ["sugar", "diabetes", "bp", "blood pressure", "hypertension", "thyroid"]
}


def extract_symptoms(text: str) -> Dict[str, Any]:
    """
    Extracts structured clinical concepts from English, Hindi, or Hinglish text.
    """
    lower = text.lower()
    extracted = {
        "symptoms": [],
        "patient_demographic": "adult",
        "duration": None,
        "is_elderly": False,
        "raw_text": text
    }

    # Detect symptoms
    for sym_category, keywords in SYMPTOM_LEXICON.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower):
                if sym_category not in extracted["symptoms"]:
                    extracted["symptoms"].append(sym_category)
                break

    # Detect demographic
    if "elderly" in extracted["symptoms"]:
        extracted["is_elderly"] = True
        extracted["patient_demographic"] = "elderly"
    elif "child" in extracted["symptoms"]:
        extracted["patient_demographic"] = "child"

    # Detect duration
    duration_patterns = [
        (r'(\d+)\s*(din|days?|hafte|weeks?|ghante|hours?)', r'\1 \2'),
        (r'(aaj|today|kal|yesterday|parso)', r'\1')
    ]
    for pattern, _ in duration_patterns:
        match = re.search(pattern, lower)
        if match:
            extracted["duration"] = match.group(0)
            break

    return extracted


def determine_follow_up(
    user_input: str,
    conversation_history: List[ConversationTurn],
    extracted: Dict[str, Any]
) -> Optional[str]:
    """
    Decides whether a targeted follow-up question is needed.
    Limits follow-ups to maximum 1 or 2 targeted questions to optimize response time.
    """
    # Count how many assistant follow-up questions have already been asked
    prior_questions = sum(1 for turn in conversation_history if turn.role == "assistant")
    if prior_questions >= 2:
        return None  # Max questions reached, proceed to triage

    combined_text = " ".join([turn.content for turn in conversation_history] + [user_input]).lower()

    # Case 1: Fever + Cough reported, need to rule out acute breathing difficulty / chest pain
    has_fever_cough = ("fever" in extracted["symptoms"] or "cough" in extracted["symptoms"])
    has_addressed_breathing = any(term in combined_text for term in ["saans", "breath", "chest", "seene", "dard nahi", "no breathing", "koi dikkat nahi"])

    if has_fever_cough and not has_addressed_breathing and prior_questions == 0:
        return (
            "Kya unko saans lene me koi dikkat ho rahi hai ya tez seene me dard hai? "
            "(Are they experiencing any breathing difficulty or chest pain?)"
        )

    # Case 2: Wound reported, need to check if bleeding is controlled or infected
    if "wound" in extracted["symptoms"]:
        has_addressed_bleeding = any(term in combined_text for term in ["bleed", "khoon", "ruk gaya", "bandage", "infection", "pus"])
        if not has_addressed_bleeding and prior_questions == 0:
            return (
                "Ghav se khoon to nahi nikal raha, ya bas regular patti/dressing ki zaroorat hai? "
                "(Is the wound bleeding actively, or does it require regular dressing/cleaning?)"
            )

    # Case 3: Very brief / vague complaint (e.g., just "tabiyat kharab hai" or "feeling sick")
    if len(extracted["symptoms"]) == 0 and prior_questions == 0:
        return (
            "Kripya thoda vistar me batayein — mukhya pareshani kya hai (jaise bukhar, dard, ya kamjori) aur kitne samay se hai? "
            "(Please describe the main symptoms like fever, pain, or weakness, and since how long?)"
        )

    return None
