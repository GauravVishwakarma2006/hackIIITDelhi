"""
Module 3: Multi-Criteria Caregiver Matcher & Ranking Engine.
Computes geodesic distances and optimizes caregiver selection across:
Score = 0.35 * Language + 0.30 * Proximity + 0.20 * Skill + 0.15 * Rating
Strictly conforms to official IIITD CAI rubric:
- 60 caregiver profiles loaded, exactly 8 inactive filtered out (52 active candidates).
- Returns Top 1 to 3 caregivers with plain-language explainability reason.
- Emergency path completely skips matching and returns empty list [].
"""

import csv
import json
import math
import os
from typing import List, Dict, Any, Optional
from app.schemas import MatchedCaregiver, Location


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates in kilometers.
    """
    R = 6371.0  # Earth's radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def load_caregivers(data_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Loads caregiver profiles from CSV or JSON.
    Guarantees consistent schema and active profile filtering.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "data", "caregivers.json")
    csv_path = os.path.join(base_dir, "data", "official_caregivers.csv")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif os.path.exists(csv_path):
        caregivers = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                is_active = row.get("active", "").strip().lower() == "true"
                caregivers.append({
                    "caregiver_id": row["caregiver_id"],
                    "id": row["caregiver_id"],
                    "name": row["name"],
                    "role": row["role"],
                    "qualification": row.get("qualification", ""),
                    "gender": row.get("gender", ""),
                    "languages": [l.strip() for l in row["languages"].split(";") if l.strip()],
                    "skills": [s.strip() for s in row["skills"].split(";") if s.strip()],
                    "base_area": row.get("base_area", ""),
                    "location": {
                        "lat": float(row["base_lat"]),
                        "lng": float(row["base_lng"])
                    },
                    "max_radius_km": float(row["max_radius_km"]) if row.get("max_radius_km") else 10.0,
                    "tier": row.get("tier", ""),
                    "rating": float(row["rating"]) if row.get("rating") else 4.0,
                    "experience_years": int(row["experience_years"]) if row.get("experience_years") else 0,
                    "free_from": row.get("free_from", "09:00"),
                    "free_until": row.get("free_until", "17:00"),
                    "active": is_active
                })
        return caregivers
    return []


def calculate_language_score(caregiver_languages: List[str], detected_lang: str) -> float:
    """Calculates Language Score (0.0 to 1.0) based on patient linguistic context."""
    cg_langs_lower = [l.lower() for l in caregiver_languages]
    norm_detected = detected_lang.lower().strip()

    if norm_detected in ["hindi", "hinglish", "hi"]:
        if "hindi" in cg_langs_lower:
            return 1.0
        if any(d in cg_langs_lower for d in ["haryanvi", "bhojpuri", "punjabi"]):
            return 0.8
        if "english" in cg_langs_lower:
            return 0.6
        return 0.2
    elif norm_detected in ["english", "en"]:
        if "english" in cg_langs_lower:
            return 1.0
        if "hindi" in cg_langs_lower:
            return 0.7
        return 0.2
    else:  # Auto / unspecified
        if "hindi" in cg_langs_lower and "english" in cg_langs_lower:
            return 1.0
        if "hindi" in cg_langs_lower or "english" in cg_langs_lower:
            return 0.9
        return 0.5


def calculate_skill_score(care_type: str, caregiver: Dict[str, Any]) -> float:
    """Calculates Skill Score (0.0 to 1.0) based on procedure requirements."""
    skills = [s.lower() for s in caregiver.get("skills", [])]
    role = caregiver.get("role", "")

    if care_type == "teleconsultation":
        if role == "doctor":
            return 1.0
        return 0.0

    if care_type == "lab_test_home":
        if role == "phlebotomist":
            if "home_phlebotomy" in skills or "sample_collection" in skills:
                return 1.0
            return 0.85
        return 0.0

    if care_type == "home_nursing":
        if role == "medic":
            key_nursing = {"wound_dressing", "catheter_care", "injection_iv", "injection_im", "post_surgical_care"}
            if any(s in key_nursing for s in skills):
                return 1.0
            return 0.85
        return 0.0

    if care_type == "paramedic_home_visit":
        if role == "medic":
            key_paramedic = {"vitals_monitoring", "bp_sugar_check", "elderly_care", "nebulization"}
            if any(s in key_paramedic for s in skills):
                return 1.0
            return 0.85
        return 0.0

    return 0.5


def rank_caregivers(
    care_type: str,
    patient_loc: Location,
    detected_language: str = "English",
    top_k: int = 3
) -> List[MatchedCaregiver]:
    """
    Ranks available active caregivers according to the official CAI evaluation formula:
    Score = 0.35 * Language + 0.30 * Proximity + 0.20 * Skill + 0.15 * Rating
    Returns top 1-3 candidates with plain-language explainability reason string.
    """
    if care_type == "emergency_112":
        return []

    caregivers = load_caregivers()
    candidates = []

    # Map Care Type to Caregiver Role
    target_role = "doctor" if care_type == "teleconsultation" else (
        "phlebotomist" if care_type == "lab_test_home" else "medic"
    )

    for cg in caregivers:
        # Filter out inactive caregivers (8 inactive out of 60)
        active_flag = cg.get("active")
        if active_flag is False or str(active_flag).strip().lower() in ["false", "0", "no"]:
            continue

        if cg.get("role") != target_role:
            continue

        cg_lat = cg["location"]["lat"]
        cg_lng = cg["location"]["lng"]
        dist_km = haversine_distance(patient_loc.lat, patient_loc.lng, cg_lat, cg_lng)

        # Proximity filter for in-person home visits
        max_r = cg.get("max_radius_km", 10.0)
        if care_type != "teleconsultation" and dist_km > max_r:
            continue

        # 1. Language Component (Weight: 0.35)
        lang_score = calculate_language_score(cg.get("languages", []), detected_language)

        # 2. Proximity Component (Weight: 0.30)
        if care_type == "teleconsultation":
            prox_score = max(0.5, round(1.0 - (dist_km / 35.0), 3))
        else:
            prox_score = max(0.1, round(1.0 - (dist_km / max(max_r, 15.0)), 3))

        # 3. Skill Component (Weight: 0.20)
        skill_score = calculate_skill_score(care_type, cg)

        # 4. Rating Component (Weight: 0.15)
        raw_rating = float(cg.get("rating", 4.0))
        rating_score = min(1.0, max(0.0, raw_rating / 5.0))

        # Official Weighted Rubric Score
        total_score = round(
            (0.35 * lang_score) +
            (0.30 * prox_score) +
            (0.20 * skill_score) +
            (0.15 * rating_score),
            2
        )

        # Plain-Language Explainability Reason String
        primary_lang = "Hindi-speaking" if "Hindi" in cg.get("languages", []) else "English-speaking"
        if "Hindi" in cg.get("languages", []) and "English" in cg.get("languages", []):
            primary_lang = "Hindi & English speaking"

        free_from = cg.get("free_from", "09:00")
        free_until = cg.get("free_until", "17:00")

        if care_type == "teleconsultation":
            reason = f"{primary_lang}, free {free_from}–{free_until}, rating {raw_rating:.1f}"
        else:
            reason = f"{primary_lang}, {dist_km:.1f} km away, free {free_from}–{free_until}, rating {raw_rating:.1f}"

        candidates.append({
            "caregiver": cg,
            "score": total_score,
            "dist_km": dist_km,
            "reason": reason
        })

    # Sort descending by score, tiebreak with proximity (closest first) and rating
    candidates.sort(key=lambda x: (x["score"], -x["dist_km"], x["caregiver"].get("rating", 0)), reverse=True)

    results = []
    for c in candidates[:top_k]:
        cg = c["caregiver"]
        results.append(
            MatchedCaregiver(
                caregiver_id=cg["caregiver_id"],
                score=c["score"],
                reason=c["reason"],
                name=cg.get("name"),
                role=cg.get("role"),
                distance_km=c["dist_km"],
                available_slot=f"{cg.get('free_from')}–{cg.get('free_until')}",
                rating=cg.get("rating")
            )
        )

    return results
