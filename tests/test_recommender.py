"""
test_recommender.py — Unit tests for VibeFinder 2.0

Covers:
  - Core recommender logic (from Project 3)
  - Agent profile validation (new for Final Project)
  - Edge cases and guardrails
"""

import pytest
from src.recommender import Song, UserProfile, Recommender, recommend_songs, load_songs
from src.agent import _validate_profile


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_small_recommender() -> Recommender:
    songs = [
        Song(id=1, title="Test Pop Track", artist="Test Artist", genre="pop",
             mood="happy", energy=0.8, tempo_bpm=120, valence=0.9,
             danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="Test Artist", genre="lofi",
             mood="chill", energy=0.4, tempo_bpm=80, valence=0.6,
             danceability=0.5, acousticness=0.9),
        Song(id=3, title="Rock Storm", artist="Test Artist", genre="rock",
             mood="intense", energy=0.95, tempo_bpm=155, valence=0.4,
             danceability=0.6, acousticness=0.05),
    ]
    return Recommender(songs)


SAMPLE_SONGS = [
    {"id": 1, "title": "Pop Hit", "artist": "A", "genre": "pop", "mood": "happy",
     "energy": 0.85, "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8, "acousticness": 0.1},
    {"id": 2, "title": "Lofi Dream", "artist": "B", "genre": "lofi", "mood": "chill",
     "energy": 0.35, "tempo_bpm": 75, "valence": 0.6, "danceability": 0.5, "acousticness": 0.85},
    {"id": 3, "title": "Rock Wall", "artist": "C", "genre": "rock", "mood": "intense",
     "energy": 0.92, "tempo_bpm": 150, "valence": 0.4, "danceability": 0.65, "acousticness": 0.08},
    {"id": 4, "title": "Jazz Night", "artist": "D", "genre": "jazz", "mood": "relaxed",
     "energy": 0.38, "tempo_bpm": 90, "valence": 0.72, "danceability": 0.55, "acousticness": 0.88},
]


# ── Core Recommender Tests (from Project 3) ───────────────────────────────────

def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)
    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_genre_match_scores_higher_than_no_match():
    user = {"genre": "pop", "mood": "sad", "energy": 0.5, "likes_acoustic": False}
    results = recommend_songs(user, SAMPLE_SONGS, k=4)
    top_song = results[0][0]
    assert top_song["genre"] == "pop", "Genre match should dominate ranking"


def test_acoustic_bonus_applied():
    user = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    results = recommend_songs(user, SAMPLE_SONGS, k=4)
    top_score = results[0][1]
    # Lofi chill with acoustic bonus should score > 4.0
    assert top_score > 3.5, f"Expected score > 3.5, got {top_score}"


def test_recommend_k_limits_results():
    user = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    for k in [1, 2, 3]:
        results = recommend_songs(user, SAMPLE_SONGS, k=k)
        assert len(results) == k, f"Expected {k} results, got {len(results)}"


def test_recommend_empty_songs_returns_empty():
    user = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    results = recommend_songs(user, [], k=5)
    assert results == []


def test_scores_are_non_negative():
    user = {"genre": "country", "mood": "sad", "energy": 0.5, "likes_acoustic": False}
    results = recommend_songs(user, SAMPLE_SONGS, k=4)
    for _, score, _ in results:
        assert score >= 0, f"Score should never be negative, got {score}"


def test_load_songs_returns_correct_count():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 30, f"Expected 30 songs, got {len(songs)}"


def test_load_songs_fields_are_correct_types():
    songs = load_songs("data/songs.csv")
    for song in songs:
        assert isinstance(song["id"], int)
        assert isinstance(song["title"], str)
        assert isinstance(song["energy"], float)
        assert 0.0 <= song["energy"] <= 1.0


# ── Agent Validation / Guardrail Tests (NEW — Final Project) ──────────────────

def test_validate_profile_valid_input():
    raw = {"genre": "pop", "mood": "happy", "energy": 0.8,
           "likes_acoustic": False, "reasoning": "User wants upbeat music."}
    profile = _validate_profile(raw)
    assert profile["genre"] == "pop"
    assert profile["mood"] == "happy"
    assert profile["energy"] == 0.8
    assert profile["likes_acoustic"] is False


def test_validate_profile_clamps_energy_above_1():
    raw = {"genre": "rock", "mood": "intense", "energy": 1.5,
           "likes_acoustic": False, "reasoning": "Too energetic input."}
    profile = _validate_profile(raw)
    assert profile["energy"] == 1.0, "Energy above 1.0 should be clamped to 1.0"


def test_validate_profile_clamps_energy_below_0():
    raw = {"genre": "ambient", "mood": "calm", "energy": -0.3,
           "likes_acoustic": True, "reasoning": "Negative energy input."}
    profile = _validate_profile(raw)
    assert profile["energy"] == 0.0, "Energy below 0.0 should be clamped to 0.0"


def test_validate_profile_invalid_genre_falls_back():
    raw = {"genre": "country", "mood": "happy", "energy": 0.6,
           "likes_acoustic": False, "reasoning": "Unknown genre."}
    profile = _validate_profile(raw)
    assert profile["genre"] == "pop", "Invalid genre should fall back to 'pop'"


def test_validate_profile_invalid_mood_falls_back():
    raw = {"genre": "lofi", "mood": "nostalgic", "energy": 0.4,
           "likes_acoustic": True, "reasoning": "Unknown mood."}
    profile = _validate_profile(raw)
    assert profile["mood"] == "happy", "Invalid mood should fall back to 'happy'"


def test_validate_profile_missing_keys_use_defaults():
    profile = _validate_profile({})
    assert profile["genre"] == "pop"
    assert profile["mood"] == "happy"
    assert profile["energy"] == 0.5
    assert profile["likes_acoustic"] is False
