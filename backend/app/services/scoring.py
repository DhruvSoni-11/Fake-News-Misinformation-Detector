"""
app/services/scoring.py
------------------------
Rule-based credibility scoring engine.

Scoring philosophy
──────────────────
We start from a neutral baseline of 100 and apply a series of evidence-based
deductions and bonuses.  The final score is clamped to [0, 100] and mapped to
a human-readable label.

Score components
────────────────
1. Keyword penalties
   • HIGH_RISK keywords   → −WEIGHT_HIGH_RISK   per unique keyword  (cap: 40 pts)
   • MEDIUM_RISK keywords → −WEIGHT_MEDIUM_RISK  per unique keyword  (cap: 20 pts)
   • LOW_RISK keywords    → −WEIGHT_LOW_RISK     per unique keyword  (cap: 10 pts)

2. Sentiment adjustment
   • Very negative tone is a strong signal of sensationalism → large penalty
   • Neutral tone suggests factual reporting → bonus
   • Very positive is also mildly suspicious (hype/propaganda) → small penalty

3. Article length bonus/penalty
   • Very short texts (<50 words) are often headlines or social posts with
     no supporting evidence → penalty
   • Long-form articles (>600 words) are more likely to be investigative → bonus

4. Repetition penalty
   • High top-word frequency indicates low-quality, padded content → penalty

All weights and thresholds are imported from core/constants.py so they can
be tuned without touching this file.
"""

from __future__ import annotations

import logging

from app.core.constants import (
    # Keywords
    HIGH_RISK_KEYWORDS,
    MEDIUM_RISK_KEYWORDS,
    LOW_RISK_KEYWORDS,
    # Weights
    WEIGHT_HIGH_RISK,
    WEIGHT_MEDIUM_RISK,
    WEIGHT_LOW_RISK,
    # Sentiment penalties / bonuses
    SENTIMENT_PENALTY_STRONG_NEG,
    SENTIMENT_PENALTY_MILD_NEG,
    SENTIMENT_BONUS_NEUTRAL,
    SENTIMENT_BONUS_MILD_POS,
    SENTIMENT_PENALTY_STRONG_POS,
    # Length
    LENGTH_BONUS_LONG,
    LENGTH_BONUS_MEDIUM,
    LENGTH_PENALTY_SHORT,
    # Repetition
    REPETITION_PENALTY_HIGH,
    REPETITION_PENALTY_MEDIUM,
    # Classification thresholds
    THRESHOLD_LIKELY_REAL,
    THRESHOLD_SUSPICIOUS,
    LABEL_LIKELY_REAL,
    LABEL_SUSPICIOUS,
    LABEL_FAKE,
)
from app.services.nlp_service import NLPResult
from app.utils.helpers import clamp
from app.utils.text_cleaner import top_word_frequency

logger = logging.getLogger(__name__)


# ── Internal scoring helpers ──────────────────────────────────────────────────

def _keyword_penalty(detected: list[str]) -> float:
    """
    Calculate total keyword penalty from the list of detected keywords.

    Each detected keyword is looked up in the risk lists and penalised
    according to its tier.  Caps prevent any single tier from wiping out
    the entire score.
    """
    high_hits  = [kw for kw in detected if kw in HIGH_RISK_KEYWORDS]
    medium_hits = [kw for kw in detected if kw in MEDIUM_RISK_KEYWORDS]
    low_hits   = [kw for kw in detected if kw in LOW_RISK_KEYWORDS]

    penalty  = min(len(high_hits)   * WEIGHT_HIGH_RISK,   40.0)
    penalty += min(len(medium_hits) * WEIGHT_MEDIUM_RISK, 20.0)
    penalty += min(len(low_hits)    * WEIGHT_LOW_RISK,    10.0)

    logger.debug(
        "Keyword penalty — high: %d hits (−%.1f) | medium: %d hits (−%.1f) | low: %d hits (−%.1f)",
        len(high_hits), min(len(high_hits) * WEIGHT_HIGH_RISK, 40),
        len(medium_hits), min(len(medium_hits) * WEIGHT_MEDIUM_RISK, 20),
        len(low_hits), min(len(low_hits) * WEIGHT_LOW_RISK, 10),
    )
    return penalty


def _sentiment_adjustment(polarity: float) -> float:
    """
    Return a signed adjustment value (+bonus or −penalty) based on
    the article's sentiment polarity.
    """
    if polarity <= -0.5:
        return -SENTIMENT_PENALTY_STRONG_NEG
    if polarity <= -0.1:
        return -SENTIMENT_PENALTY_MILD_NEG
    if polarity <= 0.1:
        return +SENTIMENT_BONUS_NEUTRAL
    if polarity <= 0.5:
        return +SENTIMENT_BONUS_MILD_POS
    # polarity > 0.5 → suspiciously positive (hype, propaganda)
    return -SENTIMENT_PENALTY_STRONG_POS


def _length_adjustment(word_count: int) -> float:
    """
    Return a signed adjustment based on article word count.
    Longer articles are generally more credible (more evidence provided).
    """
    if word_count < 50:
        return -LENGTH_PENALTY_SHORT
    if word_count <= 600:
        return +LENGTH_BONUS_MEDIUM
    return +LENGTH_BONUS_LONG


def _repetition_penalty(filtered_tokens: list[str]) -> float:
    """
    Penalise articles that repeat the same word excessively.
    High repetition often indicates spam, low-quality writing, or AI-generated filler.
    """
    freq = top_word_frequency(filtered_tokens)
    if freq > 0.05:  # top word > 5 % of all words
        return REPETITION_PENALTY_HIGH
    if freq > 0.03:  # top word 3–5 %
        return REPETITION_PENALTY_MEDIUM
    return 0.0


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_score(nlp_result: NLPResult) -> float:
    """
    Compute and return the credibility score (0–100) for the article
    described by *nlp_result*.

    Algorithm
    ---------
    score = 100
          − keyword_penalty
          + sentiment_adjustment   (signed)
          + length_adjustment      (signed)
          − repetition_penalty

    The result is clamped to [0, 100].
    """
    score: float = 100.0

    kw_pen  = _keyword_penalty(nlp_result.keywords_detected)
    sent_adj = _sentiment_adjustment(nlp_result.sentiment_polarity)
    len_adj  = _length_adjustment(nlp_result.word_count)
    rep_pen  = _repetition_penalty(nlp_result.filtered_tokens)

    score -= kw_pen
    score += sent_adj
    score += len_adj
    score -= rep_pen

    final = round(clamp(score), 2)

    logger.debug(
        "Score breakdown — base: 100 | kw_pen: −%.1f | sent_adj: %.1f | "
        "len_adj: %.1f | rep_pen: −%.1f → final: %.2f",
        kw_pen, sent_adj, len_adj, rep_pen, final,
    )
    return final


def classify(score: float) -> str:
    """
    Map a numeric credibility score to a human-readable label.

    Thresholds (from core/constants.py):
      ≥ THRESHOLD_LIKELY_REAL → "Likely Real"
      ≥ THRESHOLD_SUSPICIOUS  → "Suspicious"
      < THRESHOLD_SUSPICIOUS  → "Fake"
    """
    if score >= THRESHOLD_LIKELY_REAL:
        return LABEL_LIKELY_REAL
    if score >= THRESHOLD_SUSPICIOUS:
        return LABEL_SUSPICIOUS
    return LABEL_FAKE
