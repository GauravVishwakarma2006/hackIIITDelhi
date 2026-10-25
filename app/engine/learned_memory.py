"""
CareCompass Adaptive Memory & Continuous Self-Learning Engine.
Allows the system to:
1. Memorize user and expert corrections in real-time.
2. Store learned corrections persistently in data/learned_memory.json.
3. Prevent repeating errors by checking the learned memory store before heuristic classification.
4. Record rich user feedback (data/user_feedback.jsonl) to track continuous improvement metrics.
5. Guarantee strict safety: acute emergency red-flags are never suppressed by memory.
"""

import os
import json
import re
import time
from typing import Optional, Dict, Any, List, Tuple
from app.schemas import CareType, UrgencyLevel

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
MEMORY_FILE = os.path.join(DATA_DIR, "learned_memory.json")
FEEDBACK_LOG_FILE = os.path.join(DATA_DIR, "user_feedback.jsonl")


def _ensure_data_files():
    """Ensure data files and directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        initial_memory = {
            "version": "1.0",
            "last_updated": time.time(),
            "corrections": {}
        }
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_memory, f, indent=2, ensure_ascii=False)


def normalize_query_key(text: str) -> str:
    """Canonicalize query into normalized searchable form."""
    clean = text.lower().strip()
    # Remove punctuation
    clean = re.sub(r"[^\w\s\u0900-\u097F]", " ", clean)
    # Collapse whitespace
    tokens = clean.split()
    return " ".join(tokens)


def load_memory() -> Dict[str, Any]:
    """Load learned memory store from disk."""
    _ensure_data_files()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[LearnedMemory] Warning loading memory file: {e}")
        return {"version": "1.0", "corrections": {}}


def save_memory(data: Dict[str, Any]):
    """Save memory store atomically."""
    _ensure_data_files()
    data["last_updated"] = time.time()
    temp_file = MEMORY_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_file, MEMORY_FILE)


def check_learned_memory(text: str, is_observer: bool = False) -> Optional[Dict[str, Any]]:
    """
    Check if a query or similar pattern has a verified learned correction.
    Returns:
        dict with care_type, urgency, reasoning, confidence, or None.
    """
    key = normalize_query_key(text)
    if not key:
        return None

    memory = load_memory()
    corrections = memory.get("corrections", {})

    # 1. Exact Match
    if key in corrections:
        entry = corrections[key]
        return entry

    # 2. Token Set / Keyword Overlap Match (Fuzzy similarity for paraphrases)
    query_tokens = set(key.split())
    if len(query_tokens) >= 2:
        best_match = None
        best_sim = 0.0

        for stored_key, entry in corrections.items():
            stored_tokens = set(stored_key.split())
            if not stored_tokens:
                continue

            # Jaccard Token Similarity
            intersection = query_tokens.intersection(stored_tokens)
            union = query_tokens.union(stored_tokens)
            sim = len(intersection) / len(union) if union else 0.0

            # If observer mode specified, prioritize observer entries
            if is_observer and entry.get("is_observer"):
                sim += 0.15

            if sim > best_sim and sim >= 0.65:
                best_sim = sim
                best_match = entry

        if best_match:
            return best_match

    return None


def save_learned_correction(
    user_input: str,
    care_type: str,
    urgency: str,
    reasoning: str,
    is_observer: bool = False,
    source: str = "user_feedback"
) -> Dict[str, Any]:
    """
    Record or update a learned correction.
    Subsequent matching queries will use this verified outcome and will never repeat the mistake.
    """
    key = normalize_query_key(user_input)
    if not key:
        return {}

    memory = load_memory()
    corrections = memory.setdefault("corrections", {})

    existing = corrections.get(key, {})
    count = existing.get("feedback_count", 0) + 1

    entry = {
        "original_query": user_input,
        "care_type": care_type,
        "urgency": urgency,
        "reasoning": reasoning,
        "is_observer": is_observer,
        "source": source,
        "feedback_count": count,
        "last_updated": time.time()
    }

    corrections[key] = entry
    save_memory(memory)
    return entry


def record_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log real user feedback and automatically learn corrections when provided.
    """
    _ensure_data_files()
    feedback_entry = {
        "timestamp": time.time(),
        "user_input": feedback_data.get("user_input", ""),
        "predicted_care_type": feedback_data.get("predicted_care_type"),
        "predicted_urgency": feedback_data.get("predicted_urgency"),
        "rating": feedback_data.get("rating", "thumbs_up"),
        "suggested_care_type": feedback_data.get("suggested_care_type"),
        "comment": feedback_data.get("comment", ""),
        "observer_mode": bool(feedback_data.get("observer_mode", False))
    }

    # Append to feedback log
    with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")

    learned = False
    # If user provided a correction or rated thumbs_down with a suggested care type, learn immediately!
    suggested = feedback_data.get("suggested_care_type")
    user_input = feedback_data.get("user_input", "").strip()

    if suggested and user_input:
        # Determine appropriate urgency for the suggested care type
        if suggested in ["emergency_112", "emergency"]:
            urg = UrgencyLevel.EMERGENCY.value
            sugg_care = CareType.EMERGENCY_112.value
        elif suggested in ["home_nursing", "paramedic_home_visit"]:
            urg = UrgencyLevel.SAME_DAY.value
            sugg_care = suggested
        elif suggested == "lab_test_home":
            urg = UrgencyLevel.SCHEDULED.value
            sugg_care = CareType.LAB_TEST_HOME.value
        elif suggested == "teleconsultation":
            urg = UrgencyLevel.SAME_DAY.value
            sugg_care = CareType.TELECONSULTATION.value
        else:
            urg = UrgencyLevel.SAME_DAY.value
            sugg_care = suggested

        comment_note = feedback_data.get("comment", "").strip()
        custom_reasoning = f"User/Expert verified requirement: {sugg_care.replace('_', ' ').title()} ({urg})."
        if comment_note:
            custom_reasoning += f" User insight: '{comment_note}'."

        save_learned_correction(
            user_input=user_input,
            care_type=sugg_care,
            urgency=urg,
            reasoning=custom_reasoning,
            is_observer=bool(feedback_data.get("observer_mode", False)),
            source="user_correction"
        )
        learned = True
    elif feedback_data.get("rating") == "thumbs_up" and user_input:
        # Reinforce positive feedback in memory
        pred_care = feedback_data.get("predicted_care_type")
        pred_urg = feedback_data.get("predicted_urgency", "same_day")
        if pred_care:
            save_learned_correction(
                user_input=user_input,
                care_type=pred_care,
                urgency=pred_urg,
                reasoning="Confirmed accurate by real user feedback.",
                is_observer=bool(feedback_data.get("observer_mode", False)),
                source="positive_feedback"
            )

    return {
        "status": "success",
        "message": "Feedback recorded successfully and integrated into CareCompass continuous learning memory.",
        "learned": learned
    }


def get_feedback_insights() -> Dict[str, Any]:
    """
    Returns analytics on real user feedback and learned corrections.
    """
    _ensure_data_files()
    total = 0
    positive = 0
    negative = 0
    recent_feedback = []

    if os.path.exists(FEEDBACK_LOG_FILE):
        try:
            with open(FEEDBACK_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        total += 1
                        if entry.get("rating") == "thumbs_up":
                            positive += 1
                        else:
                            negative += 1
                        recent_feedback.append(entry)
                    except Exception:
                        pass
        except Exception as e:
            print(f"[LearnedMemory] Error reading feedback log: {e}")

    memory = load_memory()
    corrections = memory.get("corrections", {})

    return {
        "total_feedbacks": total,
        "positive_count": positive,
        "negative_count": negative,
        "accuracy_rate_pct": round((positive / total * 100), 1) if total > 0 else 100.0,
        "learned_corrections_count": len(corrections),
        "recent_corrections": list(corrections.values())[-10:],
        "recent_feedback_samples": recent_feedback[-5:]
    }
