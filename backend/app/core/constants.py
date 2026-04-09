"""
app/core/constants.py
---------------------
Domain constants: fake-news indicator keywords, scoring weights and
classification thresholds.  All magic numbers belong here — never
hard-coded inside business logic.
"""

from __future__ import annotations

# ── Sensationalist / Misinformation-Indicator Keywords ───────────────────────
# These words commonly appear in clickbait and misinformation.
# Each list is weighted differently in the scoring engine (see scoring.py).

# High-risk: strongly associated with fabricated or misleading content
HIGH_RISK_KEYWORDS: list[str] = [
    "shocking", "unbelievable", "you won't believe", "mind-blowing",
    "miracle", "secret", "they don't want you to know", "exposed",
    "conspiracy", "cover-up", "hidden truth", "leaked", "banned",
    "censored", "deep state", "new world order", "illuminati",
    "chemtrails", "microchip", "5g", "plandemic", "scamdemic",
    "hoax", "fabricated", "fake news", "mainstream media lies",
    "wake up", "sheeple", "crisis actor", "false flag",
]

# Medium-risk: sensationalist but not exclusively misinformation
MEDIUM_RISK_KEYWORDS: list[str] = [
    "viral", "breaking", "urgent", "exclusive", "bombshell",
    "stunning", "jaw-dropping", "explosive", "outrageous",
    "scandalous", "alarming", "terrifying", "devastating",
    "must read", "share before deleted", "going viral",
    "unprecedented", "historic", "revolution", "celebrity",
    "insider", "anonymous source", "sources say",
]

# Low-risk: mildly subjective but found in legitimate journalism too
LOW_RISK_KEYWORDS: list[str] = [
    "allegedly", "rumoured", "claim", "claims", "reportedly",
    "unconfirmed", "speculation", "some say", "many believe",
    "could be", "might be", "possibly", "perhaps",
]

# ── Scoring Weights ───────────────────────────────────────────────────────────
# How many points each keyword match deducts from the base score of 100.
WEIGHT_HIGH_RISK: float = 6.0
WEIGHT_MEDIUM_RISK: float = 3.0
WEIGHT_LOW_RISK: float = 1.5

# Sentiment-polarity adjustments
# Strong negative sentiment often correlates with sensationalism
SENTIMENT_PENALTY_STRONG_NEG: float = 10.0   # polarity < -0.5
SENTIMENT_PENALTY_MILD_NEG: float = 5.0      # polarity in [-0.5, -0.1)
SENTIMENT_BONUS_NEUTRAL: float = 5.0         # polarity in [-0.1, 0.1]
SENTIMENT_BONUS_MILD_POS: float = 2.0        # polarity in (0.1, 0.5]
# Strong positive is also mildly suspicious (hype)
SENTIMENT_PENALTY_STRONG_POS: float = 3.0    # polarity > 0.5

# Article-length bonuses (longer articles tend to be more substantive)
LENGTH_BONUS_LONG: float = 5.0    # > 600 words
LENGTH_BONUS_MEDIUM: float = 2.0  # 200-600 words
LENGTH_PENALTY_SHORT: float = 5.0 # < 50 words (almost no content)

# Repetition penalty — excessive word repetition signals low-quality writing
REPETITION_PENALTY_HIGH: float = 8.0    # top-word frequency > 5 %
REPETITION_PENALTY_MEDIUM: float = 4.0  # top-word frequency 3–5 %

# ── Classification Thresholds ────────────────────────────────────────────────
THRESHOLD_LIKELY_REAL: int = 65    # score >= 65  → "Likely Real"
THRESHOLD_SUSPICIOUS: int = 40     # score in [40, 65) → "Suspicious"
# score < 40 → "Fake"

LABEL_LIKELY_REAL: str = "Likely Real"
LABEL_SUSPICIOUS: str = "Suspicious"
LABEL_FAKE: str = "Fake"

# ── Sentiment Label Mapping ───────────────────────────────────────────────────
SENTIMENT_VERY_NEGATIVE: str = "Very Negative"
SENTIMENT_NEGATIVE: str = "Negative"
SENTIMENT_NEUTRAL: str = "Neutral"
SENTIMENT_POSITIVE: str = "Positive"
SENTIMENT_VERY_POSITIVE: str = "Very Positive"
