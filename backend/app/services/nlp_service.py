"""
app/services/nlp_service.py
----------------------------
NLP processing pipeline:
  - Tokenisation        (regex-based, zero external corpora required)
  - Stopword removal    (built-in 175-word English stopword set)
  - Keyword detection   (fake-news indicators from core/constants.py)
  - Sentiment analysis  (TextBlob — works out-of-the-box, no NLTK corpus needed)

Design choice: we deliberately avoid NLTK punkt / stopwords corpora so the
service starts with NO network calls after `pip install`.  All resources are
embedded here or in core/constants.py.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from textblob import TextBlob  # type: ignore

from app.core.constants import (
    HIGH_RISK_KEYWORDS,
    MEDIUM_RISK_KEYWORDS,
    LOW_RISK_KEYWORDS,
    SENTIMENT_VERY_NEGATIVE,
    SENTIMENT_NEGATIVE,
    SENTIMENT_NEUTRAL,
    SENTIMENT_POSITIVE,
    SENTIMENT_VERY_POSITIVE,
)

logger = logging.getLogger(__name__)


# ── Built-in English stopword set ─────────────────────────────────────────────
# 175 most common English stopwords — avoids any NLTK corpus download.

_STOPWORDS: frozenset[str] = frozenset({
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "arent", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "cant",
    "cannot", "could", "couldnt", "did", "didnt", "do", "does", "doesnt",
    "doing", "dont", "down", "during", "each", "few", "for", "from",
    "further", "get", "got", "had", "hadnt", "has", "hasnt", "have",
    "havent", "having", "he", "hed", "hell", "hes", "her", "here",
    "heres", "hers", "herself", "him", "himself", "his", "how", "hows",
    "i", "id", "ill", "im", "ive", "if", "in", "into", "is", "isnt",
    "it", "its", "itself", "just", "lets", "like", "me", "more",
    "most", "mustnt", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shant", "she", "shed", "shell",
    "shes", "should", "shouldnt", "so", "some", "such", "than", "that",
    "thats", "the", "their", "theirs", "them", "themselves", "then",
    "there", "theres", "these", "they", "theyd", "theyll", "theyre",
    "theyve", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasnt", "we", "wed", "well", "were", "weve",
    "were", "werent", "what", "whats", "when", "whens", "where",
    "wheres", "which", "while", "who", "whos", "whom", "why", "whys",
    "will", "with", "wont", "would", "wouldnt", "you", "youd", "youll",
    "youre", "youve", "your", "yours", "yourself", "yourselves",
    # extras useful for news text
    "said", "says", "according", "also", "one", "two", "three", "new",
    "year", "years", "last", "first", "time", "may", "can", "now",
    "still", "even", "made", "make", "us", "get", "back", "people",
})


# ── Data Transfer Object ──────────────────────────────────────────────────────

@dataclass
class NLPResult:
    """Carries all NLP artefacts produced by ``analyse``."""

    tokens: list[str] = field(default_factory=list)
    filtered_tokens: list[str] = field(default_factory=list)   # stopwords removed
    keywords_detected: list[str] = field(default_factory=list)
    sentiment_label: str = SENTIMENT_NEUTRAL
    sentiment_polarity: float = 0.0
    sentiment_subjectivity: float = 0.0
    word_count: int = 0


# ── Internal helpers ──────────────────────────────────────────────────────────

# Regex that extracts only alphabetic tokens
_TOKEN_RE = re.compile(r"[a-z]+")


def _tokenise(text: str) -> list[str]:
    """
    Tokenise *text* into lowercase alphabetic tokens.

    Uses a simple regex instead of NLTK punkt so no corpus download is needed.
    Pure punctuation and numeric tokens are excluded automatically.
    """
    return _TOKEN_RE.findall(text.lower())


def _remove_stopwords(tokens: list[str]) -> list[str]:
    """Filter English stopwords from *tokens* using the built-in set."""
    return [t for t in tokens if t not in _STOPWORDS]


def _detect_keywords(text: str) -> list[str]:
    """
    Scan *text* for known misinformation-indicator keywords/phrases.

    Uses case-insensitive whole-phrase regex matching so multi-word indicators
    like ``"you won't believe"`` or ``"they don't want you to know"`` are
    matched correctly even when they span punctuation.

    Returns a deduplicated list ordered by first appearance in the text.
    """
    text_lower = text.lower()
    found: list[str] = []
    seen: set[str] = set()

    # Process high-risk first so ordering reflects severity
    all_keywords: list[str] = (
        HIGH_RISK_KEYWORDS + MEDIUM_RISK_KEYWORDS + LOW_RISK_KEYWORDS
    )

    for keyword in all_keywords:
        if keyword in seen:
            continue
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        if pattern.search(text_lower):
            found.append(keyword)
            seen.add(keyword)

    return found


def _classify_sentiment(polarity: float) -> str:
    """Map a TextBlob polarity float to a human-readable label."""
    if polarity <= -0.5:
        return SENTIMENT_VERY_NEGATIVE
    if polarity <= -0.1:
        return SENTIMENT_NEGATIVE
    if polarity <= 0.1:
        return SENTIMENT_NEUTRAL
    if polarity <= 0.5:
        return SENTIMENT_POSITIVE
    return SENTIMENT_VERY_POSITIVE


# ── Public API ────────────────────────────────────────────────────────────────

def analyse(cleaned_text: str) -> NLPResult:
    """
    Run the full NLP pipeline on *cleaned_text*.

    Steps
    -----
    1. Tokenise with a regex tokenizer (no external corpus).
    2. Remove stopwords using the built-in 175-word set.
    3. Detect indicator keywords against the full cleaned text (phrase-safe).
    4. Sentiment analysis with TextBlob (works without NLTK corpus download).

    Parameters
    ----------
    cleaned_text :
        Article text after ``text_cleaner.clean_text()`` has been applied.

    Returns
    -------
    NLPResult
        Dataclass containing all extracted NLP artefacts.
    """
    if not cleaned_text.strip():
        logger.warning("nlp_service.analyse called with empty text.")
        return NLPResult()

    # 1. Tokenise
    tokens = _tokenise(cleaned_text)

    # 2. Remove stopwords
    filtered = _remove_stopwords(tokens)

    # 3. Keyword detection (operates on full text to catch multi-word phrases)
    keywords = _detect_keywords(cleaned_text)

    # 4. Sentiment (TextBlob requires no external corpus for basic sentiment)
    blob = TextBlob(cleaned_text)
    polarity: float = round(float(blob.sentiment.polarity), 4)
    subjectivity: float = round(float(blob.sentiment.subjectivity), 4)
    sentiment_label = _classify_sentiment(polarity)

    result = NLPResult(
        tokens=tokens,
        filtered_tokens=filtered,
        keywords_detected=keywords,
        sentiment_label=sentiment_label,
        sentiment_polarity=polarity,
        sentiment_subjectivity=subjectivity,
        word_count=len(tokens),
    )

    logger.debug(
        "NLP — words: %d | keywords: %d | polarity: %.3f | sentiment: %s",
        result.word_count,
        len(result.keywords_detected),
        result.sentiment_polarity,
        result.sentiment_label,
    )
    return result
