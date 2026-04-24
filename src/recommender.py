import csv  
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

def _compute_score(user: UserProfile, song: Song) -> Tuple[float, str]:
    """
    Core scoring logic for the OOP Recommender class.
    Works with Song dataclass and UserProfile dataclass.
    """
    score = 0.0
    reasons = []

    # Genre match
    if song.genre == user.favorite_genre:
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Mood match
    if song.mood == user.favorite_mood:
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy similarity
    energy_diff = abs(song.energy - user.target_energy)
    energy_score = round(1.0 * (1 - energy_diff), 3)
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score})")

    # Acoustic bonus
    if user.likes_acoustic and song.acousticness > 0.6:
        score += 0.5
        reasons.append("acoustic bonus (+0.5)")

    return round(score, 3), ", ".join(reasons)


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top-k Song objects sorted by score descending."""
        scored = []
        for song in self.songs:
            score, _ = _compute_score(user, song)
            scored.append((song, score))

        scored.sort(key=lambda x: (-x[1], x[0].title))
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return human-readable explanation for a song recommendation."""
        score, explanation = _compute_score(user, song)
        return f"Score: {score:.3f} — {explanation}"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # TODO: Implement CSV loading logic
    songs = []
    print(f"Loading songs from {csv_path}...")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = {
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': float(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
            }
            songs.append(song)
    print(f"Loaded songs: {len(songs)}")
    return songs

def _score_song_dict(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """
    Score a single song dict against user preferences dict.

    Scoring rules:
      - Genre match:       +2.0 points
      - Mood match:        +1.0 point
      - Energy similarity: +1.0 * (1 - |song_energy - target_energy|)
      - Acoustic bonus:    +0.5 if user likes_acoustic and acousticness > 0.6
    """
    score = 0.0
    reasons = []

    # Genre match
    if song['genre'] == user_prefs.get('genre'):
        score += 2.0       
        reasons.append("genre match (+2.0)")

    # Mood match — temporarily disabled for experiment
    if song['mood'] == user_prefs.get('mood'):
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy similarity
    target_energy = user_prefs.get('energy', 0.5)
    energy_diff = abs(song['energy'] - target_energy)
    energy_score = round(1.0 * (1 - energy_diff), 3)
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score})")

    # Acoustic bonus
    if user_prefs.get('likes_acoustic', False) and song['acousticness'] > 0.6:
        score += 0.5
        reasons.append("acoustic bonus (+0.5)")

    return round(score, 3), ", ".join(reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    scored = []
    for song in songs:
        score, explanation = _score_song_dict(user_prefs, song)
        scored.append((song, score, explanation))

    # Sort descending by score, use title as tiebreaker
    scored.sort(key=lambda x: (-x[1], x[0]['title']))
    return scored[:k]