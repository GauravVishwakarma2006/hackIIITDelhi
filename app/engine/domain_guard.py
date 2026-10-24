"""
CareCompass Clinical Domain Guard.
Ensures that only health-related queries receive clinical triage & caregiver matching.
Rejects non-medical inputs (e.g. math queries like 'quadratic equation', '2 + 2', code, trivia, gibberish)
and prompts the user to provide their health concern or symptoms.
"""

import re
from typing import Tuple, Optional

# Non-medical math, equations, coding, and trivia patterns
NON_HEALTH_REGEXES = [
    # Math & Equations (e.g. "2 + 2", "quaderatic equation", "algebra", "x^2 + 5x + 6")
    r"\b(?:quaderatic|quadratic|equation|algebra|calculus|geometry|trigonometry|polynomial|logarithm)\b",
    r"\b(?:pythagor(?:as|ean)|matrix|matrices|derivative|integral|integrate|differentiate|theorem|formula)\b",
    r"^\s*[-+]?\d*\.?\d+\s*[\+\-\*\/\^%]\s*[-+]?\d*\.?\d+\s*$",     # pure "2 + 2", "5 * 10", "100/4"
    r"^\s*(?:what\s+is\s+|calculate\s+|solve\s+)?[-+]?\d+\s*[\+\-\*\/]\s*\d+\s*[\?\.]*$", # "what is 2 + 2?"
    r"\b(?:solve|calculate|evaluate)\s+(?:for\s+[a-zA-Z]\b|the\s+equation|[-+0-9xXyYzZ\^\*\/\+= ]{3,})",
    r"\b[a-zA-Z]\s*\^\s*\d+\s*[\+\-]\s*\d*[a-zA-Z]?\s*=",           # e.g. "x^2 + 5x = 0"
    r"^\s*[-+0-9xXyYzZ\^\*\/\(\)\=\s]{3,}\s*$",                      # math expressions like "x + y = 10"

    # Programming & Code
    r"\b(?:python|javascript|typescript|c\+\+|java|html|css|sql|github|react|fastapi|docker)\b",
    r"\b(?:write\s*(?:a\s*)?(?:code|script|program|query|function|algorithm)|debug\s+this)\b",
    r"\b(?:binary\s*search|sorting\s*algorithm|linked\s*list|for\s*loop|while\s*loop)\b",
    r"(?:def\s+[a-zA-Z_]\w*\(|console\.log|print\([\"']|function\s+[a-zA-Z_]\w*\()",

    # General Non-Medical Trivia & Chatbot queries
    r"\b(?:who\s*is\s*(?:the\s*)?(?:president|prime\s*minister|pm|cm|chief\s*minister|king|queen))\b",
    r"\b(?:capital\s*of|weather\s*in|weather\s*forecast|cricket\s*score|football\s*match|ipl\s*score)\b",
    r"\b(?:tell\s*me\s*a\s*joke|sing\s*a\s*song|write\s*(?:an?\s*)?(?:essay|poem|story|letter|email))\b",
    r"\b(?:movie\s*review|song\s*lyrics|stock\s*price|crypto|bitcoin|share\s*market)\b",
    r"\b(?:how\s*far\s*is\s*the\s*moon|speed\s*of\s*light|tallest\s*building)\b",

    # Pure Keyboard Mash & Symbols
    r"^[^\w\s]{2,}$",
    r"^[0-9\s\+\-\*\/\=\.\,\?\!@#\$%\^&]{2,}$",
    r"^(?:asdf|qwerty|zxcv|lkjh|poiu|[a-z]{1,2})$"
]

# Comprehensive Multilingual Health Vocabulary (English, Hindi Devanagari, Hinglish)
HEALTH_VOCABULARY = [
    # Core symptoms
    "fever", "bukhar", "बुखार", "cough", "khansi", "खांसी", "cold", "sardi", "जुकाम", "pain", "dard", "दर्द",
    "headache", "sir dard", "सिर", "chest", "seene", "chhati", "छाती", "heart", "dil", "दिल",
    "stomach", "pet", "पेट", "back pain", "kamar", "कमर", "leg", "pair", "पैरों", "joint", "ghutne", "घुटने",
    "swelling", "sujan", "सूजन", "rash", "khujli", "खुजली", "allergy", "एलर्जी", "vomit", "ulti", "उल्टी",
    "nausea", "dast", "loose motion", "diarrhea", "दस्त", "constipation", "kabz", "कब्ज",
    "weak", "kamzor", "कमजोर", "chakkar", "dizziness", "चक्कर", "faint", "behosh", "बेहोश",
    "bp", "blood pressure", "बीपी", "sugar", "diabetes", "शुगर", "asthma", "dama", "दमा",
    "infection", "acidity", "gas", "stroke", "paralysis", "lakwa", "लकवा", "chot", "injury", "fracture",
    "wound", "ghav", "घाव", "bleed", "khoon", "blood", "खून", "burn", "jal", "जल", "poison", "zehar", "जहर",
    "seizure", "daure", "दौरे", "fits", "bedsore", "cancer", "covid", "typhoid", "dengue", "malaria",
    "saans", "sans", "breath", "सांस", "gala", "throat", "गला", "skin", "chamdi", "त्वचा",
    "peshab", "urine", "पेशाब", "pathri", "stone", "पथरी", "loose", "motion",

    # Care Types, Procedures & Healthcare Roles
    "doctor", "डॉक्टर", "nurse", "नर्स", "paramedic", "पैरामेडिक", "medic", "hospital", "अस्पताल",
    "clinic", "क्लीनिक", "phlebotomist", "caregiver", "sahayak", "सहायक", "medicine", "dawa", "dawai", "दवाई",
    "prescription", "parcha", "injection", "इंजेक्शन", "drip", "iv", "glucose", "dressing", "ड्रेसिंग",
    "patti", "पट्टी", "bandage", "catheter", "कैथेटर", "oxygen", "ऑक्सीजन", "ambulance", "एम्बुलेंस",
    "112", "108", "icu", "emergency", "आपातकालीन", "vitals", "checkup", "check-up", "जांच", "pulse",
    "teleconsult", "consult", "सलाह", "padosi", "guard",

    # Lab Tests & Diagnostics
    "test", "टेस्ट", "lab", "लैब", "sample", "सैंपल", "cbc", "सीबीसी", "thyroid", "थायराइड",
    "kft", "lft", "lipid", "x-ray", "xray", "एक्सरे", "mri", "एमआरआई", "ecg", "ईसीजी",
    "scan", "ultrasound", "report", "रिपोर्ट", "second opinion", "ओपिनियन",

    # Patient & Relatives Health Context
    "patient", "mareez", "मरीज", "bimar", "बीमार", "ill", "sick", "unwell", "tabiyat", "तबीयत",
    "takleef", "तकलीफ", "pareshani", "परेशानी", "elderly", "buzurg", "बुजुर्ग", "bedridden",
    "swasthya", "स्वास्थ्य", "care", "home visit", "home care", "ghar pe"
]


def check_health_domain(text: str, detected_lang: str = "auto") -> Tuple[bool, Optional[str]]:
    """
    Validates whether the user input belongs to the healthcare/medical domain.
    Returns:
        (is_health_query: bool, follow_up_or_clarification_message: Optional[str])
    """
    clean = text.lower().strip()

    # 1. Check for explicit non-health triggers (Math, Code, Trivia, Gibberish)
    for pattern in NON_HEALTH_REGEXES:
        if re.search(pattern, clean, re.IGNORECASE):
            return False, get_domain_rejection_message(detected_lang)

    # 2. Check for known health vocabulary
    has_health_keyword = any(word in clean for word in HEALTH_VOCABULARY)
    if has_health_keyword:
        return True, None

    # 3. Check for short health underspecified triggers (e.g. "help chahiye", "mummy ke liye", "i need help")
    from app.engine.intake import is_underspecified
    if is_underspecified(clean):
        return True, None

    # 4. Check for red flags or vulnerability markers
    from app.engine.red_flags import detect_red_flags, check_vulnerability, check_observer_alert
    is_em, _ = detect_red_flags(clean)
    if is_em:
        return True, None

    is_vuln, _ = check_vulnerability(clean)
    if is_vuln:
        return True, None

    is_obs, _ = check_observer_alert(clean)
    if is_obs:
        return True, None

    # If it contains zero health terms and is unrelated:
    return False, get_domain_rejection_message(detected_lang)


def get_domain_rejection_message(detected_lang: str) -> str:
    """Returns friendly out-of-domain guidance in the user's active language."""
    if detected_lang == "Hindi":
        return (
            "नमस्ते! मैं CareCompass हूँ, आपका स्वास्थ्य एवं देखभाल मार्गदर्शक। "
            "मैं गणित, सामान्य ज्ञान या गैर-चिकित्सीय प्रश्नों के बजाय केवल बीमारी के लक्षणों, "
            "डॉक्टर परामर्श, होम नर्सिंग, लैब टेस्ट या आपातकालीन सहायता में मदद कर सकता हूँ। "
            "कृपया अपनी स्वास्थ्य समस्या या लक्षण बताएं।"
        )
    elif detected_lang == "Hinglish":
        return (
            "Namaste! Main CareCompass hoon, aapka healthcare assistant. "
            "Main maths ya non-medical sawalon ke bajaye sirf health symptoms, "
            "doctor consultation, home nursing, lab tests ya emergency care me madad kar sakta hoon. "
            "Kripya apni health problem ya symptom batayein."
        )
    else: # English / auto
        return (
            "Hello! I am CareCompass, an AI care navigation assistant. "
            "I can only assist with healthcare needs such as medical symptoms, home nursing, "
            "lab tests, doctor consults, or emergency care. "
            "Please describe a health concern or symptom so I can help."
        )
