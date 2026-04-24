# 🎧 Model Card: VibeFinder 2.0

## 1. Model Name
**VibeFinder 2.0** — Extended from VibeFinder 1.0 (Module 3 base project)

---

## 2. Intended Use
VibeFinder 2.0 recommends songs from a 30-song catalog based on either:
- A structured taste profile (genre, mood, energy, acoustic preference), or
- A natural language description processed by a Claude AI agent

It is designed for educational demonstration of agentic AI workflows, not for production deployment. It assumes users can describe their listening mood in a sentence or two.

---

## 3. How the System Works

### Scoring Formula (unchanged from Project 3)
Each song receives a weighted score:
- **Genre match:** +2.0 (strongest signal)
- **Mood match:** +1.0 (session intent)
- **Energy similarity:** +1.0 × (1 − |song_energy − target_energy|)
- **Acoustic bonus:** +0.5 if user likes acoustic AND song acousticness > 0.6

### New: Agentic Layer (Final Project Extension)
When given natural language input, Claude API:
1. Reads the user's description
2. Maps it to one of 7 genres and 7 moods
3. Estimates energy (0.0–1.0) and acoustic preference
4. Returns a structured JSON profile

A guardrail function (`_validate_profile`) then:
- Clamps energy to [0.0, 1.0]
- Rejects unknown genres/moods with safe defaults
- Ensures no field is missing before passing to recommender

---

## 4. Data

- **30 songs** in `data/songs.csv` (expanded from 10 in Project 3)
- Each song: title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- **Genres:** pop (7), lofi (6), rock (4), jazz (4), synthwave (4), ambient (3), indie pop (2)
- **Moods:** happy, chill, intense, relaxed, moody, focused, calm
- Still missing: hip-hop, R&B, classical, country, K-pop, non-English music
- Pop remains the most represented genre (23% of songs), but minority genres now have 3-4 entries each

---

## 5. Strengths

- **Natural language interface:** Users no longer need to know technical genre/mood labels
- **Transparent explanations:** Every recommendation includes a score breakdown
- **Reliable guardrails:** Invalid AI outputs are caught before reaching the recommender
- **Improved minority genre coverage:** Jazz, synthwave, and ambient now have enough songs for meaningful top-5 results
- **Fully automated testing:** Test harness validates 10 cases with confidence scoring

---

## 6. Limitations and Bias

- **Genre dominance persists:** Weight +2.0 means genre almost always determines the #1 result. Energy-first or mood-first users are still underserved.
- **Binary genre/mood matching:** "Chill" and "relaxed" are treated as completely different — a jazz user who wants "chill" gets zero mood credit even though those moods overlap.
- **Claude can be wrong:** The agent sometimes misinterprets ambiguous descriptions. "I want something dark but uplifting" produced inconsistent genre choices across runs.
- **Pop bias reduced but not eliminated:** Pop still has the most songs. Pop users receive more varied top-5 results than ambient users.
- **No diversity penalty:** Same artist can appear multiple times in one recommendation list.
- **Acoustic asymmetry:** System rewards acoustic lovers (+0.5) but never penalizes highly acoustic songs for users who dislike acoustic music.
- **No user history:** System has no memory across sessions — preferences must be restated each time.

---

## 7. Evaluation

**Test Harness Results:**
- 10/10 test cases passed | Confidence Score: 100%

**Key test findings:**
- TC-01 to TC-04: Genre match correctly dominates for all standard profiles ✅
- TC-07: Synthwave niche profile now surfaces synthwave songs (dataset expansion fixed this) ✅
- TC-08: Adversarial profile (calm + high energy) → genre still wins, energy score only +0.38 ⚠️ known limitation
- TC-09: No negative scores even for completely unknown genres ✅

**Agent accuracy (manual testing, 12 prompts):**
- 10/12 prompts produced a profile that felt intuitively correct
- 2 prompts with highly ambiguous language ("something different", "not too much") produced reasonable but not perfect results
- All 12 passed the validation guardrail without crashing

---

## 8. Reflection and Ethics

**What are the limitations or biases in your system?**
The genre weight creates a filter bubble. A user who has always listened to pop will keep getting pop recommendations. There is no mechanism for cross-genre discovery or serendipity. The dataset also skews toward Western mainstream pop music, which disadvantages users with global or niche taste.

**Could your AI be misused, and how would you prevent that?**
The system is low-risk since it only recommends fictional songs. In a real deployment, the main misuse risk would be using the genre bias to unfairly promote certain artists or genres. Mitigation: add a diversity penalty that prevents the same artist from appearing more than once per recommendation list, and periodically audit genre distribution in results.

**What surprised you while testing reliability?**
The adversarial profile (calm mood + high energy) was the most revealing test. Despite a direct contradiction in the user's preferences, the system returned a confident answer without any warning. This showed that confidence scoring alone is not enough — the system should detect internal contradictions and flag them to the user.

**Describe your collaboration with AI during this project:**

*Helpful AI moment:* When designing the guardrail for agent output, Claude suggested clamping energy to [0.0, 1.0] AND checking for string vs float type mismatches. This caught a bug where Claude API occasionally returned energy as a string like `"0.8"` instead of a float — something I would not have anticipated.

*Flawed AI moment:* Claude initially suggested using `similarity_score = 1 - cosine_distance(genre_vector, user_vector)` as a replacement for binary genre matching. This sounded sophisticated, but testing revealed it would require a fixed vocabulary of genres mapped to a vector space — significantly more complexity for a minor improvement in edge cases. I kept the simpler binary match because it is easier to test, explain, and audit.

---

## 9. Future Work

1. **Soft genre/mood similarity:** Use an embedding model to give partial credit for similar genres ("indie pop" and "pop" share 50% credit).
2. **Diversity penalty:** Prevent the same artist from appearing twice in one top-5 list.
3. **Expand to 100+ songs:** Cover hip-hop, R&B, classical, and non-English genres.
4. **Memory across sessions:** Store user profiles so the agent improves over multiple conversations.
5. **Contradiction detection:** Flag when the user's mood and energy preferences conflict, and ask for clarification rather than guessing.
