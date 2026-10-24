"""
Module 2: Clinical Triage & Urgency Classification Engine.
Determines Care Type (emergency, paramedic_home_visit, nurse, gp_teleconsult, specialist),
Urgency Level (immediate, same_day, routine), and generates plain-language clinical reasoning.
"""

from typing import Dict, Any, Tuple
from app.schemas import CareType, UrgencyLevel


def classify_triage(
    extracted_symptoms: Dict[str, Any],
    is_emergency: bool,
    red_flags: list
) -> Tuple[str, str, str]:
    """
    Returns:
        (care_type: str, urgency: str, reasoning: str)
    """
    symptoms = extracted_symptoms.get("symptoms", [])
    duration = extracted_symptoms.get("duration", "unspecified duration")
    is_elderly = extracted_symptoms.get("is_elderly", False)
    raw = extracted_symptoms.get("raw_text", "")

    # 1. Emergency Gate (Zero-tolerance)
    if is_emergency:
        flags_str = ", ".join(red_flags)
        return (
            CareType.EMERGENCY.value,
            UrgencyLevel.IMMEDIATE.value,
            f"Life-threatening red-flag detected ({flags_str}). Immediate emergency medical intervention required via 108/112 ambulance or nearest ICU."
        )

    # 2. Nursing Care (Procedures, dressings, injections, catheter, wounds)
    if "wound" in symptoms or "injection_iv" in symptoms:
        procs = []
        if "wound" in symptoms:
            procs.append("wound management/dressing")
        if "injection_iv" in symptoms:
            procs.append("clinical administration (injection/IV/catheter)")
        procs_str = " and ".join(procs)
        return (
            CareType.NURSE.value,
            UrgencyLevel.SAME_DAY.value,
            f"Clinical nursing care indicated for home-based {procs_str} to ensure sterile, safe treatment without hospital travel."
        )

    # 3. Paramedic Home Visit (Elderly fever, vitals check, acute respiratory check, physical exam)
    if ("fever" in symptoms and is_elderly) or ("respiratory" in symptoms and is_elderly) or ("elderly" in symptoms and "fever" in symptoms):
        dur_text = f"for {duration}" if duration else "recently"
        return (
            CareType.PARAMEDIC_HOME_VISIT.value,
            UrgencyLevel.SAME_DAY.value,
            f"Acute febrile presentation in an elderly patient {dur_text}. Home paramedic dispatch recommended for immediate in-person vitals evaluation (blood pressure, SpO2, and temperature) and stabilization."
        )

    # 4. Specialist (Cardiology, Orthopedics, Chronic progressive)
    if "joint_ortho" in symptoms or ("chronic" in symptoms and "chest_pain" not in symptoms):
        return (
            CareType.SPECIALIST.value,
            UrgencyLevel.ROUTINE.value,
            "Specialized clinical consultation indicated for localized musculoskeletal or chronic metabolic condition management."
        )

    # 5. General Physician Teleconsultation (Mild fever/cough in adults, stomach ache, routine infection)
    if "fever" in symptoms or "cough" in symptoms or "stomach" in symptoms or not symptoms:
        return (
            CareType.GP_TELECONSULT.value,
            UrgencyLevel.SAME_DAY.value,
            "Stable symptoms without respiratory distress or hemodynamic compromise; highly suitable for same-day General Physician teleconsultation and prescription."
        )

    # Default fallback
    return (
        CareType.GP_TELECONSULT.value,
        UrgencyLevel.SAME_DAY.value,
        "Initial General Physician teleconsultation recommended to assess symptoms and advise further clinical investigation."
    )
