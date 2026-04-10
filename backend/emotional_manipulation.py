# emotional_manipulation.py
# Detects emotional manipulation, sensationalism, and bias in news text.
# Uses keyword heuristics + transformers sentiment analysis (no model training needed).

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Sensationalist / emotionally charged keyword patterns
# ---------------------------------------------------------------------------
SENSATIONAL_PATTERNS = [
    # Urgency / fear
    r"\b(BREAKING|URGENT|ALERT|EXCLUSIVE|SHOCKING|BOMBSHELL|SCANDAL)\b",
    # Extreme language
    r"\b(NEVER|ALWAYS|WORST|BEST|GREATEST|DISASTROUS|CATASTROPHIC|EXPLOSIVE)\b",
    # Conspiracy / unverified claims
    r"\b(they don'?t want you to know|secret agenda|hidden truth|cover.?up|deep state|fake media)\b",
    # Emotional manipulation verbs
    r"\b(OUTRAGE|ENRAGE|TERRIF|HORRIF|APPALL|DISGUST)\w*\b",
    # Clickbait punctuation
    r"[!]{2,}",
    r"\?{2,}",
    # All-caps words (3+ chars)
    r"\b[A-Z]{3,}\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SENSATIONAL_PATTERNS]


def _count_sensational_hits(text: str) -> dict:
    """Return counts and matched snippets for each pattern category."""
    labels = [
        "urgency_keywords",
        "extreme_language",
        "conspiracy_phrases",
        "emotional_verbs",
        "repeated_exclamation",
        "repeated_question",
        "all_caps_words",
    ]
    results = {}
    total_hits = 0
    for label, pattern in zip(labels, COMPILED_PATTERNS):
        matches = pattern.findall(text)
        results[label] = len(matches)
        total_hits += len(matches)
    results["total_hits"] = total_hits
    return results


def _sentiment_score(text: str) -> Optional[dict]:
    """
    Optional: use HuggingFace transformers for deeper sentiment analysis.
    Falls back gracefully if transformers is not installed.
    """
    try:
        from transformers import pipeline

        # Use a lightweight model — cached after first run
        classifier = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            truncation=True,
            max_length=512,
        )
        result = classifier(text[:512])[0]  # truncate for speed
        return {"label": result["label"], "confidence": round(result["score"], 3)}
    except Exception:
        return None  # Graceful fallback


def analyze_emotional_manipulation(text: str) -> dict:
    """
    Main function: analyze text for emotional manipulation signals.

    Returns:
        manipulation_score (0-100): higher = more manipulative
        risk_level: "low" | "medium" | "high"
        flags: dict of specific detected issues
        sentiment: optional transformer-based sentiment label
    """
    hits = _count_sensational_hits(text)
    total_hits = hits.pop("total_hits")

    # Normalize to 0-100 score (cap at 100)
    # Each hit contributes roughly 8 points; adjust as needed
    raw_score = min(total_hits * 8, 100)

    # Additional penalty: excessive caps ratio
    words = text.split()
    caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / max(len(words), 1)
    caps_penalty = min(caps_ratio * 50, 20)

    manipulation_score = min(int(raw_score + caps_penalty), 100)

    if manipulation_score < 25:
        risk_level = "low"
    elif manipulation_score < 55:
        risk_level = "medium"
    else:
        risk_level = "high"

    # Highlighted suspicious phrases
    suspicious_phrases = []
    for pattern in COMPILED_PATTERNS:
        for match in pattern.finditer(text):
            suspicious_phrases.append({
                "phrase": match.group(),
                "start": match.start(),
                "end": match.end(),
            })

    sentiment = _sentiment_score(text)

    return {
        "manipulation_score": manipulation_score,
        "risk_level": risk_level,
        "flags": hits,
        "suspicious_phrases": suspicious_phrases[:20],  # cap list size
        "sentiment": sentiment,
        "caps_ratio": round(caps_ratio, 3),
    }