"""
Module 2: Clinical Triage & Urgency Classification Engine.
Conforms strictly to IIITD CAI ground truth care types and urgencies:
- emergency_112 (urgency: emergency)
- home_nursing (urgency: same_day)
- teleconsultation (urgency: same_day)
- paramedic_home_visit (urgency: same_day)
- lab_test_home (urgency: scheduled)
"""

from typing import Tuple
from app.schemas import CareType, UrgencyLevel


def classify_triage(user_input: str, is_emergency: bool = False, red_flags: list = None) -> Tuple[str, str, str]:
    """
    Returns:
        (care_type: str, urgency: str, reasoning: str)
    """
    text = user_input.lower().strip()

    # 1. Emergency
    if is_emergency:
        flags_str = ", ".join(red_flags) if red_flags else "chest_pain, breathlessness"
        return (
            CareType.EMERGENCY_112.value,
            UrgencyLevel.EMERGENCY.value,
            f"Red-flag symptoms detected ({flags_str}); routed to emergency services, not home care."
        )

    # 2. Lab Test Home (Sample collection, CBC, Thyroid, Blood Sugar, Full body checkup)
    lab_keywords = [
        "checkup", "चेकअप", "sample", "सैंपल", "cbc", "सीबीसी", "thyroid", "थायराइड",
        "sugar test", "शुगर टेस्ट", "blood sugar test", "sugar test ghar pe", "full body"
    ]
    if any(k in text for k in lab_keywords):
        return (
            CareType.LAB_TEST_HOME.value,
            UrgencyLevel.SCHEDULED.value,
            "Diagnostic test requested; home sample collection; urgency assessed as scheduled."
        )

    # 3. Home Nursing (Injection, bedsore, dressing, surgery, insulin, wound)
    nursing_keywords = [
        "injection", "इंजेक्शन", "bedsore", "dressing", "ड्रेसिंग", "post-op",
        "surgery", "wound", "घाव", "insulin", "इंसुलिन", "patti", "पट्टी"
    ]
    if any(k in text for k in nursing_keywords):
        return (
            CareType.HOME_NURSING.value,
            UrgencyLevel.SAME_DAY.value,
            "Specific nursing procedure requested; Medic home visit; urgency assessed as same_day."
        )

    # 4. Teleconsultation (Acidity, gas, doctor consult, report review, second opinion on prescription)
    tele_keywords = [
        "acidity", "एसिडिटी", "gas", "reports", "रिपोर्ट", "second opinion",
        "सेकंड ओपिनियन", "consult a doctor", "doctor se consult", "doctor se baat"
    ]
    if any(k in text for k in tele_keywords):
        return (
            CareType.TELECONSULTATION.value,
            UrgencyLevel.SAME_DAY.value,
            "Non-urgent query suitable for a virtual doctor consult; urgency assessed as same_day."
        )

    # 5. Paramedic Home Visit (BP & sugar check at home, elderly weak/fever/cough for 2 days)
    paramedic_keywords = [
        "bp", "बीपी", "fever and cough", "bukhar", "बुखार", "weak", "कमजोर", "check-up", "जांच"
    ]
    if any(k in text for k in paramedic_keywords):
        return (
            CareType.PARAMEDIC_HOME_VISIT.value,
            UrgencyLevel.SAME_DAY.value,
            "General complaint suitable for a Medic home visit with optional virtual doctor consult; urgency assessed as same_day."
        )

    # Default fallback
    return (
        CareType.TELECONSULTATION.value,
        UrgencyLevel.SAME_DAY.value,
        "Non-urgent query suitable for a virtual doctor consult; urgency assessed as same_day."
    )
