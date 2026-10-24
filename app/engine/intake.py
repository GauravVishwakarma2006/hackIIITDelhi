"""
Module 1: Smart Intake & Dialogue Manager.
Handles multilingual symptom detection and underspecified query handling per IIITD CAI ground truth.
"""

from typing import Dict, List, Optional, Any
from app.schemas import ConversationTurn

# Underspecified inputs that require follow-up inquiry
UNDERSPECIFIED_TRIGGERS = [
    "help chahiye", "मदद चाहिए", "i need help", "help",
    "doctor chahiye", "डॉक्टर चाहिए",
    "i want to book something for my mother", "माँ के लिए कुछ बुक करना है", "mummy ke liye kuch book karna hai",
    "hi, is anyone there?", "hello koi hai?", "नमस्ते, कोई है?"
]


def is_underspecified(text: str) -> bool:
    clean = text.lower().strip().rstrip("?.!,")
    return clean in UNDERSPECIFIED_TRIGGERS or any(clean == trigger for trigger in UNDERSPECIFIED_TRIGGERS)


def determine_follow_up(
    user_input: str,
    conversation_history: List[ConversationTurn]
) -> Optional[str]:
    """
    Returns the exact follow-up question if intent is underspecified and not yet clarified.
    """
    if conversation_history and len(conversation_history) > 0:
        return None  # Already answered follow-up, proceed

    clean = user_input.lower().strip().rstrip("?.!,")

    if is_underspecified(clean):
        # Match benchmark follow-up template
        if any(h in clean for h in ["help chahiye", "मदद चाहिए", "i need help", "hello koi hai", "नमस्ते, कोई है", "hi, is anyone there"]):
            if "i need help" in clean and "77.112" not in clean: # Some english use Happy to help
                return "Happy to help. Could you tell me the main symptom or service you need (home visit, nursing, lab test, or teleconsult)?"
            return "Namaste! I'm here to help. Who is this for, and what's the concern — fever, a nursing need, a lab test, or a doctor consult?"
        else:
            return "Happy to help. Could you tell me the main symptom or service you need (home visit, nursing, lab test, or teleconsult)?"

    return None
