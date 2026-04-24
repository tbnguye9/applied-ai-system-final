"""
agent.py — Agentic Workflow for VibeFinder 2.0

The agent uses Claude API to:
1. Parse a natural-language mood/preference description from the user
2. Convert it into a structured UserProfile
3. Call the recommender with that profile
4. Return recommendations + explanation

This is the core AI feature for the Final Project (Agentic Workflow).
"""

import json
import logging
import os
from typing import Optional

import requests

from src.recommender import load_songs, recommend_songs

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"
VALID_GENRES = ["pop", "lofi", "rock", "jazz", "ambient", "synthwave", "indie pop"]
VALID_MOODS  = ["happy", "chill", "intense", "focused", "relaxed", "moody", "calm"]

SYSTEM_PROMPT = f"""You are a music taste analyst. Given a user's natural language description
of what they want to listen to right now, extract a structured music preference profile.

Respond ONLY with a valid JSON object — no markdown, no explanation, no backticks.

The JSON must have exactly these keys:
- "genre": one of {VALID_GENRES}
- "mood": one of {VALID_MOODS}
- "energy": a float between 0.0 (very calm) and 1.0 (very energetic)
- "likes_acoustic": true or false
- "reasoning": one sentence explaining your interpretation

If the user's description is unclear or contradictory, make the best reasonable guess
and note the uncertainty in "reasoning".
"""


def _call_claude(user_message: str, api_key: str) -> dict:
    """
    Call Claude API and return parsed JSON profile.
    Raises ValueError if response cannot be parsed.
    """
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": MODEL,
        "max_tokens": 300,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
    }

    logger.info("Calling Claude API to interpret user preferences...")
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(f"Claude API error {response.status_code}: {response.text}")

    raw_text = response.json()["content"][0]["text"].strip()
    logger.info(f"Claude raw response: {raw_text}")

    # Strip markdown fences if present
    clean = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def _validate_profile(profile: dict) -> dict:
    """
    Validate and sanitize the profile returned by Claude.
    Falls back to safe defaults for invalid values.
    """
    safe = {}

    genre = profile.get("genre", "pop").lower()
    safe["genre"] = genre if genre in VALID_GENRES else "pop"

    mood = profile.get("mood", "happy").lower()
    safe["mood"] = mood if mood in VALID_MOODS else "happy"

    try:
        energy = float(profile.get("energy", 0.5))
        safe["energy"] = max(0.0, min(1.0, energy))
    except (TypeError, ValueError):
        safe["energy"] = 0.5

    safe["likes_acoustic"] = bool(profile.get("likes_acoustic", False))
    safe["reasoning"] = str(profile.get("reasoning", "No reasoning provided."))

    return safe


def run_agent(user_input: str, api_key: str, k: int = 5, csv_path: str = "data/songs.csv") -> dict:
    """
    Full agentic pipeline:
      1. Parse user natural language → structured profile (via Claude)
      2. Validate profile (guardrail)
      3. Load songs from CSV
      4. Run recommender
      5. Return structured result

    Returns a dict with keys:
      - "profile": the validated user profile
      - "reasoning": Claude's interpretation note
      - "recommendations": list of (song_dict, score, explanation)
      - "error": str or None
    """
    result = {"profile": None, "reasoning": "", "recommendations": [], "error": None}

    # Step 1 — Claude interprets the user's natural language
    try:
        raw_profile = _call_claude(user_input, api_key)
    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        result["error"] = f"Could not reach Claude API: {e}"
        return result

    # Step 2 — Validate / sanitize
    profile = _validate_profile(raw_profile)
    result["profile"] = profile
    result["reasoning"] = profile.pop("reasoning", "")

    logger.info(f"Validated profile: {profile}")

    # Step 3 & 4 — Load songs and recommend
    try:
        songs = load_songs(csv_path)
        recommendations = recommend_songs(profile, songs, k=k)
        result["recommendations"] = recommendations
        logger.info(f"Recommender returned {len(recommendations)} songs.")
    except Exception as e:
        logger.error(f"Recommender error: {e}")
        result["error"] = f"Recommender failed: {e}"

    return result


def format_agent_output(user_input: str, result: dict) -> str:
    """Pretty-print the agent result to terminal."""
    lines = []
    lines.append("\n" + "=" * 70)
    lines.append(f"  🤖 VIBEFINDER AGENT")
    lines.append("=" * 70)
    lines.append(f"  User said: \"{user_input}\"")

    if result.get("error"):
        lines.append(f"\n  ❌ Error: {result['error']}")
        return "\n".join(lines)

    profile = result.get("profile", {})
    lines.append(f"\n  🧠 Claude interpreted this as:")
    lines.append(f"     Genre:         {profile.get('genre')}")
    lines.append(f"     Mood:          {profile.get('mood')}")
    lines.append(f"     Energy:        {profile.get('energy')}")
    lines.append(f"     Likes Acoustic:{profile.get('likes_acoustic')}")
    lines.append(f"     Reasoning:     {result.get('reasoning')}")

    lines.append(f"\n  🎵 Top {len(result['recommendations'])} Recommendations:")
    for i, (song, score, explanation) in enumerate(result["recommendations"], 1):
        lines.append(f"\n  #{i}: {song['title']} — {song['artist']}")
        lines.append(f"       Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        lines.append(f"       Score: {score:.3f}")
        lines.append(f"       Why:   {explanation}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
