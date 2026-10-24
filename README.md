# 🛰️ HackIIITDelhi: Autonomous Internship & Opportunity Radar

An intelligent web-agent system built for **Hack IIIT Delhi**, powered by [TinyFish](https://tinyfish.ai). It autonomously discovers, browses, and extracts structured internship, job, and hackathon opportunities across company career pages with precision schema validation.

---

## ⚡ Features

- **Autonomous Web Navigation**: TinyFish agents dynamically scroll, click, and inspect modern career portals (JavaScript-rendered, SPA, and bot-protected sites).
- **Parallel Multi-Agent Scraping**: Concurrently queries multiple career destinations (Jane Street, Google Careers, Microsoft Careers, Razorpay, etc.) using `AsyncTinyFish`.
- **Dynamic Search Discovery**: Integrates TinyFish search to proactively query the web for freshly posted opportunities and automatically dispatches worker agents to target pages.
- **Strict JSON Schema Output**: Guarantees deterministic role metadata:
  - Role Title
  - Company / Source
  - Location
  - Remote vs On-site status
  - Application Deadline
  - Direct Application Link

---

## 🛠️ Tech Stack

- **Agent Orchestration**: TinyFish SDK (`tinyfish` >= 0.11.0)
- **Runtime**: Python 3.12+ / `asyncio`
- **Configuration**: `python-dotenv`

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/GauravVishwakarma2006/hackIIITDelhi.git
cd hackIIITDelhi
```

### 2. Set up Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory (copied from `.env.example`):
```bash
TINYFISH_API_KEY=your_tinyfish_api_key_here
```

---

## 💻 Running the Stages

### Stage 1: Single-Agent Inspection
Runs a single autonomous agent on Jane Street open roles:
```bash
python radar.py 1
```

### Stage 2: Parallel Multi-Target Agent Scrape
Dispatches parallel worker agents to scrape top tech careers in concurrent sessions and compiles `internships.json`:
```bash
python radar.py 2
```

### Stage 3: Autonomous Web Search & Agent Dispatch
Uses free TinyFish search discovery to find fresh 2026 internship postings across the web, then dispatches agents to extract structured data:
```bash
python radar.py 3
```

---

## 🔒 Security Note
API keys and secrets are protected via `.gitignore` and must **never** be committed to source control.
