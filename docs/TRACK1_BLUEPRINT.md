# 🧭 CareCompass: AI-Powered Care Navigation & Caregiver Matching
### Track 1: System Flow, Clinical Architecture & Implementation Blueprint
**Hack IIITD — Centre for Artificial Intelligence (CAI), IIIT-Delhi**  
**Track:** AI for Healthcare Access  
**Problem Statement:** CareCompass — Intelligent, Multilingual Care Navigation & Safety-First Matching

---

## 1. Problem Context & Vision

Healthcare in India suffers from severe triage friction:
- **Over-triage:** Patients rush to emergency departments for minor illnesses manageable via home care or telemedicine.
- **Under-triage:** Critical red-flag signs (acute chest pain, stroke signs, dyspnea) are delayed due to confusion or home remedies.
- **Language Barrier:** Millions express symptoms in colloquial Hindi or Hinglish (*"Papa ko do din se bukhar hai aur khansi bhi"*), which standard diagnostic forms fail to parse.
- **Mismatch:** Caregiver dispatching is manual and lacks intelligent multi-constraint optimization (skills, geographic distance, language match, availability, and clinical ratings).

**CareCompass** is an end-to-end, API-first conversational care navigation system engineered for speed, safety, explainability, and accessibility (including voice support for elderly and low-literacy users).

---

## 2. Core Architecture & End-to-End Workflow

CareCompass is built around a **Safety-First, 3-Stage Pipeline**:

```
[User Request (Text / Voice)] (English, Hindi, Hinglish)
            │
            ▼
┌───────────────────────────────────────────────┐
│       Module 1: Multilingual Smart Intake     │
│ - Language Normalization & Entity Extraction │
│ - Red Flag Rule Gate (Zero Latency Check)     │
└───────────────────────┬───────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │ Red Flag Detected?        │
         YES                         NO
          │                           │
          ▼                           ▼
┌──────────────────────────┐  ┌───────────────────────────────────┐
│ 🚨 Emergency Escalation   │  │ Sufficient Info (<3 Follow-ups)?  │
│ - Skip Matching          │  └─────────┬─────────────────────────┘
│ - Immediate 108 Guidance │           YES                        NO
└──────────────────────────┘            │                          │
                                        ▼                          ▼
                         ┌─────────────────────────────┐  ┌───────────────────┐
                         │   Module 2: Triage Engine   │  │ Targeted Follow-up│
                         │ - Care Type & Urgency       │  │ Question to User  │
                         │ - Plain-Language Reasoning  │  └───────────────────┘
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │ Module 3: Caregiver Matcher │
                         │ - Multi-objective Ranking   │
                         │ - Skill, Dist, Lang, Slot   │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   1-Tap Booking Dashboard   │
                         └─────────────────────────────┘
```

---

## 3. Module Breakdown & Technical Specification

### Module 1: Multilingual Smart Intake
- **Language Ingestion:** Automatically detects and normalizes English, Hindi, and Hinglish phrases (*"bukhar"*, *"chhati me dard"*, *"saans phoolna"*, *"vomiting"*, *"chot lag gayi"*).
- **Entity & Symptom Extraction:** Identifies primary complaint, duration, severity, and associated comorbidities (e.g., diabetes, hypertension).
- **Adaptive Dialogue Manager:** Evaluates clinical completeness. If critical information is missing, asks a maximum of **2 to 3 targeted follow-ups** (e.g., asking about breathing difficulty when cough and fever are reported).
- **Voice Support:** Speech-to-Text and Text-to-Speech support for low-literacy and elderly accessibility.

### Module 2: Clinical Triage & Safety Engine (Zero Tolerance for Under-Triage)
- **Care Types:**
  1. `emergency`: Red-flag escalation with clear call-for-help guidance.
  2. `paramedic_home_visit`: Acute vitals check, severe fever, elderly immobility.
  3. `nurse`: Wound dressings, catheterization, injection/IV administration.
  4. `gp_teleconsult`: Mild non-urgent cough/cold, general follow-ups, minor rash.
  5. `specialist`: Chronic progressive, cardiology, neurology, pediatric/orthopedic concerns.
- **Urgency Levels:** `immediate` (emergencies/red flags), `same_day` (acute infections/wounds), `routine` (preventive/mild).
- **Rule-Based Clinical Safety Gate (Pre-LLM):** Red-flag detector runs deterministic validation on emergency keywords (e.g., *saans phoolna*, *seene me dard*, *unresponsive*, *blood in sputum*) so that emergency recall is **100% guaranteed** before classification even touches probabilistic models.

### Module 3: Multi-Criteria Caregiver Matcher
Given patient coordinates $(lat_p, lng_p)$, required care type $C$, patient language $L_p$, and time window $T$:
$$\text{Score}(CG_i) = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{dist}} \cdot S_{\text{distance}} + w_{\text{lang}} \cdot S_{\text{language}} + w_{\text{rate}} \cdot S_{\text{rating}} + w_{\text{slot}} \cdot S_{\text{slot}}$$
- **Distance ($S_{\text{distance}}$):** Haversine distance penalty $e^{-\lambda \cdot d_{\text{km}}}$.
- **Language ($S_{\text{language}}$):** Bonus for native language alignment (critical for elder care in Delhi NCR).
- **Explainability:** Each match outputs a human-readable justification (e.g., *"Hindi-speaking, 2.8 km away, available today at 4:00 PM, 4.9 rating"*).

---

## 4. REST API Schema Compliance (IIITD CAI Contract)

### `POST /api/v1/triage`
```json
{
  "user_input": "papa ko do din se bukhar hai aur khansi bhi",
  "language": "auto",
  "location": { "lat": 28.54, "lng": 77.27 },
  "conversation_history": []
}
```

### Response (Follow-up Needed)
```json
{
  "follow_up_question": "Kya unko saans lene me koi dikkat ho rahi hai ya tez seene me dard hai? (Are they experiencing any breathing difficulty or chest pain?)",
  "care_type": null,
  "urgency": null,
  "red_flags": [],
  "reasoning": "Need to rule out acute respiratory distress before finalizing triage.",
  "matched_caregivers": []
}
```

### Response (Final Decision & Match)
```json
{
  "follow_up_question": null,
  "care_type": "paramedic_home_visit",
  "urgency": "same_day",
  "red_flags": [],
  "reasoning": "Fever with productive cough for 2 days in elderly patient, stable vitals check advised; no acute respiratory distress reported.",
  "matched_caregivers": [
    {
      "caregiver_id": "CG_014",
      "score": 0.94,
      "reason": "Certified paramedic, speaks Hindi & English, 2.8 km away, available today at 4:00 PM"
    },
    {
      "caregiver_id": "CG_029",
      "score": 0.88,
      "reason": "Home-care nurse, speaks Hindi, 4.1 km away, available today at 5:30 PM"
    }
  ]
}
```
