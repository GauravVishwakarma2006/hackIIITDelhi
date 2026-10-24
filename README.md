# 🧭 CareCompass: AI-Powered Care Navigation & Caregiver Matching
> **Hack IIITD — Centre for Artificial Intelligence (CAI), IIIT-Delhi**  
> **Track**: AI for Healthcare Access  
> **Problem Statement**: Understand what a patient needs and connect them to the right caregiver, quickly and safely.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Safety Recall](https://img.shields.io/badge/Safety%20Recall-100%25-red.svg)](tests/test_safety_recall.py)

---

## 📌 Problem Overview
Patients and families in India frequently face friction navigating early healthcare:
- **Over-triage**: Patients crowd emergency rooms for minor ailments manageable via home visits or teleconsultations.
- **Under-triage**: Critical red-flag signs (e.g., chest pain, respiratory distress, stroke) are delayed or overlooked.
- **Language Barrier**: Millions communicate symptoms in colloquial Hindi or Hinglish (*"Papa ko do din se bukhar hai aur khansi bhi"*).
- **Matching Friction**: Caregiver dispatch lacks multi-criteria optimization across clinical skill, distance, language fluency, and real-time availability.

**CareCompass** provides a safety-first, multilingual triage pipeline and multi-constraint caregiver matching engine with an accessible voice-enabled interface and complete adherence to the official Hack IIITD (CAI) benchmark schema.

---

## 🏛️ System Architecture

CareCompass operates across three tightly integrated modules:

1. **Module 1: Multilingual Smart Intake & Vulnerability Gatekeeper**  
   - Accepts free text or voice input in English, Hindi (Devanagari), and Hinglish.
   - Detects patient isolation, immobility, or prolonged illness markers (*"akela hoon"*, *"uth nahi pa raha"*, *"fever 5+ days"*), automatically escalating urgency.
   - Asks targeted clinical follow-up questions for underspecified requests.

2. **Module 2: Zero-Tolerance Deterministic Safety Gate & Triage Engine**  
   - **Deterministic Pre-ML Safety Gate**: Evaluates 9 red-flag categories across English, Hindi, and Hinglish with 100% safety recall before any ML/NLP step.
   - Immediate escalation to national emergency numbers: **Helpline 112** and **Ambulance 108**, completely skipping caregiver matching.
   - **Official Care Types (5 Enums)**:
     - `emergency_112`
     - `paramedic_home_visit`
     - `home_nursing`
     - `lab_test_home`
     - `teleconsultation`
   - **Official Urgency Levels (3 Enums)**:
     - `emergency`
     - `same_day`
     - `scheduled`

3. **Module 3: Multi-Criteria Caregiver Matcher (Official Rubric Formula)**  
   - Filters out inactive helpers (evaluates 52 active profiles from 60 total).
   - Ranks available certified caregivers using the official rubric weighting breakdown:
     $$\text{Score} = 0.35 \times \text{Language} + 0.30 \times \text{Proximity} + 0.20 \times \text{Skill} + 0.15 \times \text{Rating}$$
   - Returns Top 1 to 3 caregivers with explicit plain-language explainability (e.g., *"Hindi-speaking, 2.8 km away, free 09:00–15:00, rating 4.8"*).

4. **Decoupled TinyFish Live Emergency Agent**:
   - Sub-10ms response on emergency screen: 112/108 call buttons appear instantly.
   - TinyFish asynchronous background runner fetches verified 24x7 trauma centers and emergency contacts without blocking triage execution.

---

## 🚀 Mentor-Focused Features (Edge-Case Handling)
1. **Vulnerability Escalation**: Automatically detects isolation and prolonged duration (*"akela hoon"*, *"fever 5+ days"*), escalating urgency to `same_day` / `emergency`.
2. **Family / Proxy Reporting Mode**: Allows family members living in other cities to input the patient's coordinates in Delhi NCR and match local caregivers near the patient.
3. **1-Tap WhatsApp Share**: Deep-links (`https://wa.me/?text=...`) to forward verified triage recommendations, arrival times, and emergency alerts to family members with one tap.
4. **Grandparent Accessibility UX**: Browser-native voice recognition (`webkitSpeechRecognition` with `hi-IN`) and speech synthesis read-aloud (`speechSynthesis`) requiring zero app downloads.

---

## 📂 Repository Structure

```
├── app/
│   ├── main.py                # FastAPI REST API serving /triage and /api/v1/triage
│   ├── schemas.py             # Pydantic JSON contracts (strict enums)
│   ├── tinyfish_agent.py      # Decoupled async emergency trauma lookup agent
│   ├── engine/
│   │   ├── red_flags.py       # Deterministic trilingual red-flag & vulnerability gatekeeper
│   │   ├── intake.py          # Multilingual dialogue manager & follow-up generator
│   │   └── triage.py          # Clinical care type & urgency classification
│   ├── matcher/
│   │   └── ranking.py         # Multi-criteria caregiver ranking (official 4-factor formula)
│   └── static/                # Luxury light beige & sage voice-ready frontend
├── data/
│   ├── official_caregivers.csv# Official caregiver dataset (60 rows, 52 active)
│   └── caregivers.json        # Structured caregiver profiles
├── tests/
│   ├── test_api.py            # Automated API contract & routing benchmark test suite
│   └── test_safety_recall.py  # 100% recall test across 56+ trilingual emergency cases
├── generate_predictions.py    # Generates test_predictions.csv for hidden test evaluation
├── Dockerfile                 # Containerized API environment
├── docker-compose.yml         # 1-command startup
├── requirements.txt           # Python dependencies
└── README.md                  # System documentation
```

---

## ⚡ Quickstart

### 1. Local Setup
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run API Server & UI
```bash
python -m app.main
```
Visit `http://localhost:8000` to interact with the web interface. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 3. Run Automated Tests
```bash
# Run API benchmark tests
python -m unittest tests/test_api.py

# Run 100% Emergency Safety Recall Test (56+ cases)
python -m unittest tests/test_safety_recall.py
```

### 4. Docker Deployment
```bash
docker compose up --build
```

---

## 📜 Official API Contract (IIITD CAI)

### Endpoint: `POST /triage` (also available at `POST /api/v1/triage`)

#### Request
```json
{
  "user_input": "papa ko do din se bukhar hai aur khansi bhi",
  "language": "auto",
  "location": { "lat": 28.5445, "lng": 77.2725 },
  "conversation_history": []
}
```

#### Response (Care Recommended)
```json
{
  "follow_up_question": null,
  "care_type": "paramedic_home_visit",
  "urgency": "same_day",
  "red_flags": [],
  "reasoning": "Acute symptoms/vitals check required at home; paramedic home visit assigned; urgency assessed as same_day.",
  "matched_caregivers": [
    {
      "caregiver_id": "CG_048",
      "score": 0.95,
      "reason": "Hindi & English speaking, 1.2 km away, free 08:00–14:00, rating 4.9",
      "name": "Vikram Singh",
      "role": "medic",
      "distance_km": 1.2,
      "available_slot": "08:00–14:00",
      "rating": 4.9
    }
  ]
}
```

#### Response (Emergency Escalation — 0 Caregivers Matched)
```json
{
  "follow_up_question": null,
  "care_type": "emergency_112",
  "urgency": "emergency",
  "red_flags": ["chest_pain"],
  "reasoning": "Red-flag symptoms detected (chest pain); immediately routed to national emergency services (Helpline 112 / Ambulance 108), not home care. Matching caregivers is strictly skipped for patient safety.",
  "matched_caregivers": []
}
```

#### Response (Follow-up Question Needed)
```json
{
  "follow_up_question": "Namaste! I'm here to help. Who is this for, and what's the concern — fever, a nursing need, a lab test, or a doctor consult?",
  "care_type": null,
  "urgency": null,
  "red_flags": [],
  "reasoning": "Intent underspecified — asking a follow-up before deciding care type.",
  "matched_caregivers": []
}
```

---

## 🧪 Hidden Test Predictions
When the hidden test set is released, generate `test_predictions.csv` with a single command:
```bash
python generate_predictions.py --input data/test_cases.jsonl --output test_predictions.csv
```
Columns produced: `case_id, user_input, predicted_care_type, predicted_urgency, red_flags, top_caregiver_id, score, reasoning`.
