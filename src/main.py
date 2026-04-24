"""
main.py — VibeFinder 2.0: Applied AI Music Recommender

Runs two modes:
  1. Classic mode   : python -m src.main
  2. Agent mode     : python -m src.main --agent "I want something chill to study to"

Agent mode requires ANTHROPIC_API_KEY set in environment.
"""

import argparse
import os
import sys

from tabulate import tabulate

from src.recommender import load_songs, recommend_songs
from src.agent import run_agent, format_agent_output


def print_recommendations(profile_name: str, recommendations) -> None:
    """Print top recommendations as a formatted table."""
    print(f"\n{'='*70}")
    print(f"  🎵 Profile: {profile_name}")
    print(f"{'='*70}")

    table_data = []
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        table_data.append([
            f"#{i}",
            song['title'],
            song['artist'],
            song['genre'],
            song['mood'],
            song['energy'],
            f"{score:.3f}",
            explanation
        ])

    headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score", "Reasons"]
    print(tabulate(table_data, headers=headers, tablefmt="rounded_outline"))
    print()


def run_classic_mode():
    """Run the original 6-profile recommender demo."""
    songs = load_songs("data/songs.csv")

    profiles = [
        ("High-Energy Pop",          {"genre": "pop",       "mood": "happy",   "energy": 0.8,  "likes_acoustic": False}),
        ("Chill Lofi",               {"genre": "lofi",      "mood": "chill",   "energy": 0.3,  "likes_acoustic": True}),
        ("Deep Intense Rock",        {"genre": "rock",      "mood": "intense", "energy": 0.9,  "likes_acoustic": False}),
        ("Adversarial (Calm+High)",  {"genre": "ambient",   "mood": "calm",    "energy": 0.9,  "likes_acoustic": True}),
        ("Synthwave Moody",          {"genre": "synthwave", "mood": "moody",   "energy": 0.75, "likes_acoustic": False}),
        ("Jazz Relaxed Acoustic",    {"genre": "jazz",      "mood": "relaxed", "energy": 0.37, "likes_acoustic": True}),
    ]

    print("\n🎵 VibeFinder 2.0 — Classic Mode")
    for name, prefs in profiles:
        print_recommendations(name, recommend_songs(prefs, songs, k=5))


def run_agent_mode(user_input: str):
    """Run the agentic workflow with a natural language input."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print(f"\n🤖 VibeFinder 2.0 — Agent Mode")
    result = run_agent(user_input, api_key=api_key, k=5, csv_path="data/songs.csv")
    print(format_agent_output(user_input, result))


def main():
    parser = argparse.ArgumentParser(description="VibeFinder 2.0 — AI Music Recommender")
    parser.add_argument(
        "--agent",
        type=str,
        metavar="PROMPT",
        help='Natural language music request, e.g. "I feel sad and want calm music"',
    )
    args = parser.parse_args()

    if args.agent:
        run_agent_mode(args.agent)
    else:
        run_classic_mode()


if __name__ == "__main__":
    main()
