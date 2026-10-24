"""
evaluate.py - Quantitative Evaluation Benchmark Script (Hack IIITD CAI).
Measures Safety Recall on Red Flags (20% Rubric Weight) and Routine Classification Accuracy.
Evaluates against triage_dataset.jsonl.
"""

import json
import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from triage_rules import evaluate_safety_and_vulnerability
from triage_classifier import classify_routine_care


def run_evaluation(dataset_path: str = "triage_dataset.jsonl"):
    if not os.path.exists(dataset_path):
        print(f"Dataset '{dataset_path}' not found.")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    total_emergencies = 0
    caught_emergencies = 0
    total_routine = 0
    correct_care_types = 0

    for item in records:
        text = item.get("user_input", "")
        expected_care = item.get("care_type")
        expected_urgency = item.get("urgency")

        # 1. Test Red-Flag Gatekeeper
        safety = evaluate_safety_and_vulnerability(text)
        if expected_urgency == "emergency":
            total_emergencies += 1
            if safety["is_emergency"]:
                caught_emergencies += 1

        # 2. Test Classifier
        if not safety["is_emergency"]:
            total_routine += 1
            res = classify_routine_care(text)
            pred_care = res["care_type"]
            if pred_care == expected_care:
                correct_care_types += 1

    recall = (caught_emergencies / total_emergencies) * 100 if total_emergencies else 100.0
    accuracy = (correct_care_types / total_routine) * 100 if total_routine else 100.0

    print("=" * 60)
    print(" CareCompass Benchmark Evaluation (Hack IIITD - CAI)")
    print("=" * 60)
    print(f"Total Cases Evaluated   : {len(records)}")
    print(f"Total Emergencies       : {total_emergencies}")
    print(f"Emergencies Caught      : {caught_emergencies}")
    print(f"Safety Emergency Recall : {recall:.2f}% ({caught_emergencies}/{total_emergencies})")
    print(f"Routine Cases Evaluated : {total_routine}")
    print(f"Routine Accuracy        : {accuracy:.2f}% ({correct_care_types}/{total_routine})")
    print("=" * 60)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "triage_dataset.jsonl"
    run_evaluation(path)
