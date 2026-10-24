# 🧭 CareCompass: AI-Powered Care Navigation & Caregiver Matching
> **Hack IIITD — Centre for Artificial Intelligence (CAI), IIIT-Delhi**  
> **Track**: AI for Healthcare Access  
> **Problem Statement**: Understand what a patient needs and connect them to the right caregiver, quickly and safely.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📌 Problem Overview
Patients and families often struggle to navigate healthcare options:
- **Over-triage**: Patients crowd emergency rooms for minor ailments manageable via home visits or teleconsultations.
- **Under-triage**: Critical red-flag signs (e.g., chest pain, respiratory distress) are delayed or overlooked.
- **Language Barrier**: Millions communicate symptoms in colloquial Hindi or Hinglish (*"Papa ko do din se bukhar hai aur khansi bhi"*).
- **Matching Friction**: Caregiver dispatch lacks multi-criteria optimization across clinical skill, distance, language fluency, and real-time availability.

**CareCompass** provides a safety-first, multilingual triage pipeline and multi-constraint caregiver matching engine with an accessible voice-enabled interface.

---

## 🏛️ System Architecture

CareCompass operates across three tightly integrated modules:

1. **Module 1: Multilingual Smart Intake**  
   Accepts free text or voice input in English, Hindi, and Hinglish. Asks 2 to 4 targeted clinical follow-up questions to clarify symptom duration, severity, and patient context.
2. **Module 2: Safety-First Triage Engine**  
   Deterministic red-flag safety gate + clinical classification engine to route patients into:
   - `emergency` (Immediate escalation with 108 emergency call guidance)
   - `paramedic_home_visit` (Vitals check, acute febrile illness, elderly care)
   - `nurse` (Wound dressing, IV/injection, catheter care)
   - `gp_teleconsult` (Routine respiratory, mild complaints, follow-up)
   - `specialist` (Cardiology, neurology, orthopedics, chronic disease)
3. **Module 3: Multi-Criteria Caregiver Matcher**  
   Ranks nearby available caregivers using an objective scoring function:
   $$\text{Score} = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{dist}} \cdot S_{\text{distance}} + w_{\text{lang}} \cdot S_{\text{language}} + w_{\text{rate}} \cdot S_{\text{rating}} + w_{\text{slot}} \cdot S_{\text{slot}}$$
   Every recommendation includes clear, explainable reasoning in plain language.

---

## 📂 Repository Structure

```
├── docs/
│   └── TRACK1_BLUEPRINT.md    # Track 1: System flow, clinical architecture & API contract
├── app/
│   ├── api/                   # REST API following IIITD CAI JSON schema
│   ├── engine/                # Clinical triage, red flag rules & Hinglish NLP
│   ├── matcher/               # Geodesic multi-criteria caregiver ranking
│   └── static/                # Accessible, voice-enabled web demo
├── data/
│   └── caregivers.json        # Synthetic caregiver database (Delhi NCR)
├── radar.py                   # TinyFish autonomous web discovery & scraping engine
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Containerized deployment
└── README.md                  # Project overview & quickstart
```

---

## ⚡ Quickstart

### 1. Setup Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your keys (e.g. TINYFISH_API_KEY)
```

### 3. Run the API Server & Demo
```bash
python -m app.main
```
Visit `http://localhost:8000` to interact with the conversational triage interface.

---

## 📜 Official API Contract (IIITD CAI)

### Endpoint: `POST /api/v1/triage`
**Request Payload**:
```json
{
  "user_input": "papa ko do din se bukhar hai aur khansi bhi",
  "language": "auto",
  "location": { "lat": 28.54, "lng": 77.27 },
  "conversation_history": []
}
```

**Response Payload**:
```json
{
  "follow_up_question": "Kya unko saans lene me dikkat ya tez seene me dard ho raha hai?",
  "care_type": null,
  "urgency": null,
  "red_flags": [],
  "reasoning": "Clarifying respiratory distress before finalizing care pathway.",
  "matched_caregivers": []
}
```

---

## 👥 Authors & Team
- **Gaurav Vishwakarma** — Team Lead / AI & Systems Engineering
- Built for **Hack IIITD (CAI, IIIT-Delhi)**
