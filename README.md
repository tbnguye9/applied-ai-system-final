# 🎵 VibeFinder 2.0 — Applied AI Music Recommender

> **Final Project — AI 110 | Extended from Module 3: Music Recommender Simulation**

## Project Summary

**Base Project (Module 3):** A content-based music recommender that scores songs using a weighted formula across genre, mood, energy, and acousticness — simulating how platforms like Spotify rank personalized suggestions.

**Final Extension:** VibeFinder 2.0 adds an **Agentic Workflow** powered by Claude AI. Users can now describe what they want in natural language ("I'm stressed and need something calm"), and the agent automatically interprets that into a structured taste profile, then calls the recommender. A structured **Test Harness** validates system reliability across 10 test cases with confidence scoring.

---

## Architecture Overview

```
User Input (natural language)
        │
        ▼
┌─────────────────────┐
│   Claude AI Agent   │  ← Parses intent → structured UserProfile
│   (src/agent.py)    │  ← Validates & sanitizes output (guardrail)
└────────┬────────────┘
         │ UserProfile dict
         ▼
┌─────────────────────┐
│    Recommender      │  ← Scores all 30 songs with weighted formula
│  (src/recommender.py│  ← Returns top-K with explanations
└────────┬────────────┘
         │
         ▼
  Ranked Results + Explanation
         │
         ▼
┌─────────────────────┐
│   Test Harness      │  ← 10 automated test cases
│ (tests/test_harness)│  ← Confidence score + pass/fail report
└─────────────────────┘
```

**Data flow:** Input → Agent (Claude) → Profile Validation → Recommender → Output
**AI Feature:** Agentic Workflow — the agent plans, interprets, and delegates
**Reliability:** Test Harness runs 10 predefined cases, prints confidence score

System diagram: `assets/architecture.png`

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/applied-ai-system-final.git
cd applied-ai-system-final
```

### 2. Create virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key (for agent mode only)

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Running the System

### Classic Mode (no API key needed)

Runs 6 predefined profiles through the recommender:

```bash
python -m src.main
```

### Agent Mode (requires API key)

Describe what you want in natural language:

```bash
python -m src.main --agent "I'm feeling sad and want something calm and acoustic"
python -m src.main --agent "Give me something high energy for the gym"
python -m src.main --agent "I want moody late-night vibes"
```

### Run Test Harness

```bash
python -m tests.test_harness
```

### Run Unit Tests

```bash
pytest
```

---

## Sample Interactions

**Input 1:** `"I'm feeling sad and want something calm and acoustic"`

```
🧠 Claude interpreted this as:
   Genre:         ambient
   Mood:          calm
   Energy:        0.2
   Likes Acoustic:True
   Reasoning:     User wants emotionally soothing, quiet music.

🎵 Top 5 Recommendations:
  #1: Deep Space Drift — Orbit Bloom  | Score: 4.270
  #2: Quiet Mountain — Orbit Bloom    | Score: 4.220
  #3: Coffee Shop Stories — Slow Stereo | Score: 3.370
```

**Input 2:** `"Give me something high energy for the gym"`

```
🧠 Claude interpreted this as:
   Genre:         pop
   Mood:          intense
   Energy:        0.95
   Likes Acoustic:False

🎵 Top 5 Recommendations:
  #1: Gym Hero — Max Pulse      | Score: 4.950
  #2: Pulse Rising — Max Pulse  | Score: 4.900
  #3: Headbanger Highway — Voltline | Score: 2.950
```

**Input 3:** `"Late night drive, feeling reflective and a bit dark"`

```
🧠 Claude interpreted this as:
   Genre:         synthwave
   Mood:          moody
   Energy:        0.72

🎵 Top 5 Recommendations:
  #1: Night Drive Loop — Neon Echo   | Score: 3.970
  #2: Cassette Dreams — Synth Machine | Score: 3.920
  #3: Neon Pulse — Synth Machine     | Score: 3.800
```

---

## Design Decisions

**Why Agentic Workflow?** The biggest limitation of the original recommender was that users had to supply precise genre/mood labels. Real users don't think "I want lofi chill energy 0.3" — they say "I need to focus but I'm tired." The agent bridges that gap by translating human language into machine-readable profiles.

**Why validate Claude's output?** Claude occasionally returns unexpected values (energy > 1.0, unknown genres). The `_validate_profile()` guardrail clamps and sanitizes every field before it reaches the recommender, ensuring the system never crashes from a bad AI response.

**Why expand to 30 songs?** The 10-song dataset made minority genres (synthwave, jazz) almost impossible to serve. 30 songs gives each genre 3-5 entries, making the recommender meaningfully useful for non-pop users.

**Trade-off kept from Project 3:** Genre weight (+2.0) still dominates. This was intentional — it produces predictable, explainable results that are easy to test and audit.

---

## Testing Summary

**Test Harness** (10 automated cases):

- 10/10 passed | Confidence Score: 100%
- Covers: genre dominance, acoustic bonus, score sorting, edge cases (unknown genre, conflicting preferences), explanation completeness

**Unit Tests** (15 cases via pytest):

- Core recommender logic (from Project 3)
- Agent validation guardrails (new)
- Edge cases: empty songs, invalid energy clamping, missing profile keys

**Key finding:** The adversarial profile (calm mood + high energy) still surfaces the correct genre — confirming genre weight dominates even under conflicting signals. This is a known limitation documented in `model_card.md`.

---

## Reflection

This project taught me that the hardest part of AI engineering is not the algorithm — it's the **interface between human intent and machine input**. Adding the Claude agent solved a real usability problem: now anyone can use VibeFinder in plain English instead of filling out a structured form.

I also learned that guardrails are not optional. When I tested the agent without validation, Claude occasionally returned energy values above 1.0 or used mood labels not in our dataset. One bad output would have broken the recommender silently. Building `_validate_profile()` made the system resilient to AI unpredictability.

---

## 🎬 Demo Walkthrough

[Watch Demo Walkthrough](https://www.loom.com/share/a0853d2807f2420baa06b67bbb742b34)

The walkthrough demonstrates:

- Classic mode with 3 profiles
- Agent mode with 3 natural language inputs
- Test harness run with confidence score output

---

## Repository Structure

```
applied-ai-system-final/
├── src/
│   ├── recommender.py     # Core scoring logic (from Project 3)
│   ├── agent.py           # Agentic workflow (NEW — Final Project)
│   └── main.py            # CLI runner (classic + agent mode)
├── tests/
│   ├── test_recommender.py  # 15 unit tests (pytest)
│   └── test_harness.py      # 10-case evaluation script (NEW)
├── data/
│   └── songs.csv          # 30-song dataset (expanded from 10)
├── assets/
│   └── architecture.png   # System diagram
├── model_card.md
├── requirements.txt
└── README.md
```
