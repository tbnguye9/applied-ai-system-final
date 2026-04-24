"""
test_harness.py — Evaluation Script for VibeFinder 2.0

Runs the recommender against a fixed set of test cases and prints
a structured pass/fail summary with confidence scores.

Usage:
    python -m tests.test_harness

This is the Test Harness stretch feature (+2 points).
"""

from src.recommender import load_songs, recommend_songs

# ── Test Case Definitions ─────────────────────────────────────────────────────
# Each case defines: name, user profile, and expected assertions

TEST_CASES = [
    {
        "name": "TC-01: Pop Happy Profile → top result is pop genre",
        "profile": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
        "check": lambda results: results[0][0]["genre"] == "pop",
        "description": "Genre match dominates: top song should be pop",
    },
    {
        "name": "TC-02: Lofi Chill Acoustic → acoustic bonus applied",
        "profile": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
        "check": lambda results: results[0][1] > 3.5,
        "description": "Perfect lofi match with acoustic bonus should score > 3.5",
    },
    {
        "name": "TC-03: Rock Intense → top result is rock genre",
        "profile": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
        "check": lambda results: results[0][0]["genre"] == "rock",
        "description": "Rock intense profile should surface rock songs first",
    },
    {
        "name": "TC-04: Jazz Relaxed → top result is jazz genre",
        "profile": {"genre": "jazz", "mood": "relaxed", "energy": 0.37, "likes_acoustic": True},
        "check": lambda results: results[0][0]["genre"] == "jazz",
        "description": "Jazz relaxed profile should surface jazz songs first",
    },
    {
        "name": "TC-05: Results count = k=3",
        "profile": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        "check": lambda results: len(results) == 3,
        "description": "k=3 should return exactly 3 results",
        "k": 3,
    },
    {
        "name": "TC-06: Scores are sorted descending",
        "profile": {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": False},
        "check": lambda results: all(results[i][1] >= results[i+1][1] for i in range(len(results)-1)),
        "description": "Scores must be sorted highest to lowest",
    },
    {
        "name": "TC-07: Synthwave niche genre → synthwave songs surface",
        "profile": {"genre": "synthwave", "mood": "moody", "energy": 0.75, "likes_acoustic": False},
        "check": lambda results: results[0][0]["genre"] == "synthwave",
        "description": "Niche genre users should still get genre-matched results (30-song dataset)",
    },
    {
        "name": "TC-08: Adversarial (calm + high energy) → genre still wins",
        "profile": {"genre": "ambient", "mood": "calm", "energy": 0.9, "likes_acoustic": True},
        "check": lambda results: results[0][0]["genre"] == "ambient",
        "description": "Genre dominance: even with conflicting energy, genre match should win",
    },
    {
        "name": "TC-09: All scores are non-negative",
        "profile": {"genre": "country", "mood": "sad", "energy": 0.5, "likes_acoustic": False},
        "check": lambda results: all(score >= 0 for _, score, _ in results),
        "description": "No score should ever be negative, even for unknown genres",
    },
    {
        "name": "TC-10: Explanation is non-empty for all results",
        "profile": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        "check": lambda results: all(isinstance(exp, str) and exp.strip() for _, _, exp in results),
        "description": "Every recommendation must include a non-empty explanation",
    },
]


def run_harness(csv_path: str = "data/songs.csv") -> None:
    print("\n" + "=" * 70)
    print("  🧪 VIBEFINDER 2.0 — TEST HARNESS")
    print("=" * 70)

    songs = load_songs(csv_path)
    passed = 0
    failed = 0
    results_log = []

    for tc in TEST_CASES:
        k = tc.get("k", 5)
        try:
            results = recommend_songs(tc["profile"], songs, k=k)
            ok = tc["check"](results)
        except Exception as e:
            ok = False
            results = []
            print(f"  ⚠️  Exception in {tc['name']}: {e}")

        status = "✅ PASS" if ok else "❌ FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        results_log.append((tc["name"], status, tc["description"]))

    # Print summary table
    print(f"\n  {'TEST CASE':<45} {'STATUS':<10} DESCRIPTION")
    print(f"  {'-'*45} {'-'*10} {'-'*30}")
    for name, status, desc in results_log:
        print(f"  {name:<45} {status:<10} {desc}")

    total = passed + failed
    confidence = passed / total if total > 0 else 0

    print(f"\n  ─────────────────────────────────────────────────────────────────")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"  Confidence Score: {confidence:.0%}")

    if confidence == 1.0:
        print("  🎉 All tests passed — system is reliable!")
    elif confidence >= 0.8:
        print("  ⚠️  Most tests passed — review failed cases above.")
    else:
        print("  ❌ Multiple failures — recommender logic needs attention.")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_harness()
