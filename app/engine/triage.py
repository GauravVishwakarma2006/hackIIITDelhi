"""
Module 2: Clinical Triage & Urgency Classification Engine.
Conforms strictly to IIITD CAI ground truth care types and urgencies:
- Care Types: emergency_112 | paramedic_home_visit | home_nursing | lab_test_home | teleconsultation
- Urgency Levels: emergency | same_day | scheduled
(Zero use of obsolete 'routine' or non-standard specialist labels).
"""

from typing import Tuple, List
from app.schemas import CareType, UrgencyLevel
from app.engine.red_flags import check_vulnerability


def classify_triage(
    user_input: str,
    is_emergency: bool = False,
    red_flags: List[str] = None
) -> Tuple[str, str, str]:
    """
    Classifies patient need into official Care Type, Urgency, and clinical reasoning.
    Returns:
        (care_type: str, urgency: str, reasoning: str)
    """
    text = user_input.lower().strip()
    is_vulnerable, vuln_reason = check_vulnerability(text)

    # 1. Emergency Path (Red flags triggered)
    if is_emergency:
        flags_str = ", ".join(red_flags) if red_flags else "critical emergency symptoms"
        return (
            CareType.EMERGENCY_112.value,
            UrgencyLevel.EMERGENCY.value,
            f"Red-flag symptoms detected ({flags_str}); immediately routed to Emergency Helpline 112 / 108. Home care skipped."
        )

    # 1.5. Explicit Virtual / Teleconsultation Request
    explicit_tele = [
        "teleconsultation", "teleconsult", "doctor appointment", "virtual consult",
        "doctor se consult", "doctor se baat", "consult a doctor"
    ]
    if any(k in text for k in explicit_tele) and not any(k in text for k in ["injection", "catheter", "dressing", "sample"]):
        return (
            CareType.TELECONSULTATION.value,
            UrgencyLevel.SAME_DAY.value,
            "Virtual doctor teleconsultation requested; urgency assessed as same_day."
        )

    # 2. Lab Test Home (Sample collection, CBC, Thyroid, Blood Sugar, Full body checkup)
    lab_keywords = [
        "full body checkup", "sample", "सैंपल", "cbc", "सीबीसी", "thyroid", "थायराइड",
        "sugar test", "शुगर टेस्ट", "blood sugar test", "sugar test ghar pe", "full body",
        "blood test", "रक्त जांच", "urine test", "lipid profile", "kft", "lft", "hba1c", "lab test"
    ]
    if any(k in text for k in lab_keywords):
        urgency = UrgencyLevel.SAME_DAY.value if is_vulnerable else UrgencyLevel.SCHEDULED.value
        reason = "Diagnostic lab test requested; home sample collection by phlebotomist; urgency assessed as scheduled."
        if is_vulnerable:
            reason = f"Diagnostic lab test requested. {vuln_reason}"
        return (CareType.LAB_TEST_HOME.value, urgency, reason)

    # 3. Home Nursing (Injection, bedsore, dressing, surgery, insulin, wound, catheter)
    nursing_keywords = [
        "injection", "इंजेक्शन", "bedsore", "bed sore", "dressing", "ड्रेसिंग", "post-op",
        "surgery", "wound", "घाव", "insulin", "इंसुलिन", "patti", "पट्टी", "catheter",
        "कैथेटर", "iv drip", "drip lagwani", "stiches", "टांके"
    ]
    if any(k in text for k in nursing_keywords):
        reason = "Specific nursing procedure requested; certified nurse/medic home visit; urgency assessed as same_day."
        if is_vulnerable:
            reason += f" {vuln_reason}"
        return (
            CareType.HOME_NURSING.value,
            UrgencyLevel.SAME_DAY.value,
            reason
        )

    # 4. Paramedic Home Visit (BP & sugar check at home, elderly weak/fever/cough for 2 days, immobility)
    paramedic_keywords = [
        "bp", "बीपी", "fever", "bukhar", "बुखार", "khansi", "cough", "weak", "कमजोर",
        "check-up", "जांच", "vitals", "vomiting", "उल्टी", "dast", "loose motion",
        "elderly care", "walk nahi", "uth nahi", "dizziness"
    ]
    if any(k in text for k in paramedic_keywords) or is_vulnerable:
        reason = "Acute symptoms/vitals check required at home; paramedic home visit assigned; urgency assessed as same_day."
        if is_vulnerable:
            reason = f"Acute symptoms in vulnerable patient. {vuln_reason} Paramedic home visit dispatched."
        return (
            CareType.PARAMEDIC_HOME_VISIT.value,
            UrgencyLevel.SAME_DAY.value,
            reason
        )

    # 5. Teleconsultation (Acidity, gas, doctor consult, report review, second opinion on prescription)
    tele_keywords = [
        "acidity", "एसिडिटी", "gas", "गैस", "reports", "रिपोर्ट", "second opinion",
        "सेकंड ओपिनियन", "consult a doctor", "doctor se consult", "doctor se baat",
        "teleconsult", "skin rash", "minor rash", "cold", "जुकाम", "halka bukhar", "mild"
    ]
    if any(k in text for k in tele_keywords):
        urgency = UrgencyLevel.SAME_DAY.value
        reason = "Non-emergency complaint suitable for virtual doctor teleconsultation; urgency assessed as same_day."
        return (
            CareType.TELECONSULTATION.value,
            urgency,
            reason
        )

    # Default fallback: safe teleconsultation with same_day urgency
    return (
        CareType.TELECONSULTATION.value,
        UrgencyLevel.SAME_DAY.value,
        "Non-urgent clinical inquiry suitable for virtual doctor consultation; urgency assessed as same_day."
    )


def classify_routine_care(user_input: str) -> dict:
    """
    Standard interface used by evaluate.py and generate_predictions.py.
    Returns: {"care_type": str, "urgency": str, "reasoning": str, "needs_follow_up": bool, "follow_up_question": Optional[str]}
    """
    from app.engine.intake import determine_follow_up
    follow_up = determine_follow_up(user_input, [])
    if follow_up:
        return {
            "care_type": None,
            "urgency": None,
            "reasoning": "Intent underspecified — follow-up inquiry needed.",
            "needs_follow_up": True,
            "follow_up_question": follow_up
        }

    from app.engine.domain_guard import check_health_domain
    is_health, rejection_msg = check_health_domain(user_input)
    if not is_health:
        return {
            "care_type": None,
            "urgency": None,
            "reasoning": "Non-health query detected — out of medical scope.",
            "needs_follow_up": True,
            "follow_up_question": rejection_msg
        }

    care_type, urgency, reasoning = classify_triage(user_input, is_emergency=False, red_flags=[])
    return {
        "care_type": care_type,
        "urgency": urgency,
        "reasoning": reasoning,
        "needs_follow_up": False,
        "follow_up_question": None
    }


