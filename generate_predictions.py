"""
CareCompass Hidden Test Set Prediction Generator.
Conforms strictly to Hack IIITD (CAI, IIIT-Delhi) submission requirements.
Takes an input JSONL/CSV test dataset and outputs test_predictions.csv for automated scoring:
Columns: case_id, user_input, predicted_care_type, predicted_urgency, red_flags, top_caregiver_id, score, reasoning
"""

import argparse
import csv
import json
import os
import sys
from typing import Dict, Any

from app.schemas import TriageRequest, Location
from app.main import triage_endpoint


def process_case(case: Dict[str, Any]) -> Dict[str, Any]:
    case_id = case.get("case_id", case.get("id", "UNKNOWN"))
    user_input = case.get("user_input", case.get("text", case.get("query", "")))
    language = case.get("language", "auto")

    loc_dict = case.get("location", {})
    if isinstance(loc_dict, dict) and "lat" in loc_dict and "lng" in loc_dict:
        loc = Location(lat=float(loc_dict["lat"]), lng=float(loc_dict["lng"]))
    else:
        loc = Location(lat=28.5445, lng=77.2725)

    history = case.get("conversation_history", [])

    req = TriageRequest(
        user_input=user_input,
        language=language,
        location=loc,
        conversation_history=history
    )

    resp = triage_endpoint(req)

    top_cg_id = ""
    top_score = 0.0
    if resp.matched_caregivers and len(resp.matched_caregivers) > 0:
        top_cg = resp.matched_caregivers[0]
        top_cg_id = top_cg.caregiver_id
        top_score = top_cg.score

    return {
        "case_id": case_id,
        "user_input": user_input,
        "predicted_care_type": resp.care_type or "follow_up_needed",
        "predicted_urgency": resp.urgency or "follow_up_needed",
        "red_flags": ";".join(resp.red_flags) if resp.red_flags else "none",
        "top_caregiver_id": top_cg_id,
        "score": top_score,
        "reasoning": resp.reasoning
    }


def main():
    parser = argparse.ArgumentParser(description="Generate predictions for CareCompass CAI Hackathon evaluation")
    parser.add_argument("--input", "-i", default="data/test_cases.jsonl", help="Path to input test set (JSONL format)")
    parser.add_argument("--output", "-o", default="test_predictions.csv", help="Path to output test_predictions.csv")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    cases = []
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cases.append(json.loads(line))
    else:
        # Generate sample benchmark predictions if test file not yet dropped
        print(f"Notice: Input file '{input_path}' not found. Generating predictions on internal benchmark vignettes.")
        cases = [
            {"case_id": "S0001", "user_input": "Doctor prescribed an injection, can someone come home"},
            {"case_id": "S0002", "user_input": "Mild acidity and gas since morning, want to consult a doctor"},
            {"case_id": "S0003", "user_input": "Grandmother has a bedsore that needs dressing"},
            {"case_id": "S0004", "user_input": "accident ke baad bleeding ruk nahi rahi"},
            {"case_id": "S0005", "user_input": "seene me tez dard hai aur chakkar aa raha hai"},
            {"case_id": "S0006", "user_input": "wo achanak gir gaye response nahi de rahe"},
            {"case_id": "S0007", "user_input": "mummy ka bp sugar ghar pe check karwana hai"},
            {"case_id": "S0008", "user_input": "Book a full body checkup, home collection"},
            {"case_id": "S0009", "user_input": "Ghar pe akela hoon, uth nahi pa raha aur bukhar hai 5 din se"}
        ]

    rows = [process_case(c) for c in cases]

    fieldnames = [
        "case_id", "user_input", "predicted_care_type", "predicted_urgency",
        "red_flags", "top_caregiver_id", "score", "reasoning"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {len(rows)} predictions in '{output_path}'.")


if __name__ == "__main__":
    main()
