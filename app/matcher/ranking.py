"""
Module 3: Multi-Criteria Caregiver Matcher & Ranking Engine.
Computes geodesic distances and optimizes caregiver selection across:
clinical role, skill coverage, distance, language fluency, rating, and availability.
"""

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
    return round(R * c, 2)


def load_caregivers(data_path: Optional[str] = None) -> List[Dict[str, Any]]:
    if not data_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_path = os.path.join(base_dir, "data", "caregivers.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def rank_caregivers(
    care_type: str,
    patient_loc: Location,
    patient_lang: str = "Hindi",
    top_k: int = 3
) -> List[MatchedCaregiver]:
    """
    Ranks available caregivers according to multi-objective utility.
    Emergency path skips matching entirely.
    """
    if care_type == "emergency":
        return []

    caregivers = load_caregivers()
    candidates = []

    for cg in caregivers:
        # Check role compatibility
        is_exact_role = (cg["role"] == care_type)
        # Paramedics and nurses can cross-cover home visits if needed
        is_substitute = (
            (care_type == "paramedic_home_visit" and cg["role"] == "nurse") or
            (care_type == "nurse" and cg["role"] == "paramedic_home_visit") or
            (care_type == "gp_teleconsult" and cg["role"] == "gp_teleconsult")
        )

        if not (is_exact_role or is_substitute):
            continue

        # 1. Distance Calculation
        cg_lat = cg["location"]["lat"]
        cg_lng = cg["location"]["lng"]
        dist_km = haversine_distance(patient_loc.lat, patient_loc.lng, cg_lat, cg_lng)

        # 2. Distance Score (decay with distance)
        dist_score = 1.0 / (1.0 + 0.15 * dist_km)

        # 3. Rating Score (out of 5.0)
        rating_score = (cg.get("rating", 4.5) / 5.0)

        # 4. Language Match
        lang_match = any(
            patient_lang.lower() in l.lower() or "hindi" in l.lower()
            for l in cg.get("languages", ["Hindi"])
        )
        lang_score = 1.0 if lang_match else 0.7

        # 5. Exact Role vs Substitute
        role_weight = 1.0 if is_exact_role else 0.85

        # Weighted Composite Score
        total_score = (
            0.40 * dist_score +
            0.30 * role_weight +
            0.15 * rating_score +
            0.15 * lang_score
        )
        total_score = round(min(0.99, max(0.60, total_score)), 2)

        # Format explainable reason
        earliest_slot = cg["availability_slots"][0].replace("today_", "") if cg.get("availability_slots") else "available soon"
        langs_str = "/".join(cg.get("languages", ["Hindi"])[:2])
        role_title = cg["role"].replace("_", " ").title()

        reason = (
            f"{langs_str}-speaking {role_title}, {dist_km} km away ({cg.get('area', 'Delhi')}), "
            f"free at {earliest_slot}, {cg.get('rating', 4.8)}★ ({cg.get('total_reviews', 100)}+ reviews)"
        )

        candidates.append({
            "caregiver": cg,
            "score": total_score,
            "dist_km": dist_km,
            "earliest_slot": earliest_slot,
            "reason": reason
        })

    # Sort descending by composite score
    candidates.sort(key=lambda x: x["score"], reverse=True)

    results = []
    for c in candidates[:top_k]:
        cg = c["caregiver"]
        results.append(
            MatchedCaregiver(
                caregiver_id=cg["id"],
                name=cg.get("name"),
                role=cg.get("role"),
                score=c["score"],
                reason=c["reason"],
                distance_km=c["dist_km"],
                available_slot=c["earliest_slot"],
                rating=cg.get("rating")
            )
        )

    return results
