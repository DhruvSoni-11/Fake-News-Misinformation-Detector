"""
app/utils/text_cleaner.py
-------------------------
Pure text-cleaning and normalisation utilities.
Functions are stateless and side-effect free so they're easy to test and reuse.
"""

from __future__ import annotations

import re
import unicodedata


# ── HTML / Markup ─────────────────────────────────────────────────────────────

def strip_html(text: str) -> str:
    """Remove all HTML/XML tags from *text*."""
    return re.sub(r"<[^>]+>", " ", text)


def decode_html_entities(text: str) -> str:
    """
    Replace common HTML entities with their Unicode equivalents.
    We use a lightweight regex approach to avoid a heavy dependency.
    """
    entities = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&nbsp;": " ",
        "&mdash;": "—", "&ndash;": "–", "&hellip;": "…",
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)
    return text


# ── Normalisation ─────────────────────────────────────────────────────────────

def normalise_unicode(text: str) -> str:
    """
    Convert all Unicode characters to their closest ASCII representation.
    Handles accented characters, smart quotes, em-dashes, etc.
    """
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def to_lowercase(text: str) -> str:
    """Lower-case the entire text."""
    return text.lower()


def remove_urls(text: str) -> str:
    """Strip embedded URLs (http/https/ftp) from the text body."""
    return re.sub(r"https?://\S+|ftp://\S+|www\.\S+", " ", text)


def remove_emails(text: str) -> str:
    """Remove e-mail addresses."""
    return re.sub(r"\S+@\S+\.\S+", " ", text)


def remove_special_characters(text: str) -> str:
    """
    Remove characters that are not alphanumeric, whitespace, or
    common punctuation useful for sentence structure.
    Keeps: letters, digits, spaces, period, comma, exclamation, question mark,
           apostrophe, hyphen.
    """
    return re.sub(r"[^a-z0-9\s.,!?'\-]", " ", text)


def collapse_whitespace(text: str) -> str:
    """Replace multiple consecutive whitespace characters with a single space."""
    return re.sub(r"\s+", " ", text).strip()


# ── Repetition Analysis ───────────────────────────────────────────────────────

def top_word_frequency(words: list[str]) -> float:
    """
    Return the frequency (0-1) of the single most-repeated word in *words*.
    Used by the scoring engine to detect low-quality, repetitive writing.
    """
    if not words:
        return 0.0
    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    max_count = max(freq.values())
    return max_count / len(words)


# ── Master Cleaner ────────────────────────────────────────────────────────────

def clean_text(raw: str) -> str:
    """
    Full cleaning pipeline applied in order:
      1. Decode HTML entities
      2. Strip HTML tags
      3. Remove embedded URLs and e-mails
      4. Normalise Unicode → ASCII
      5. Lowercase
      6. Remove special characters
      7. Collapse whitespace

    Returns the cleaned string ready for NLP processing.
    """
    text = decode_html_entities(raw)
    text = strip_html(text)
    text = remove_urls(text)
    text = remove_emails(text)
    text = normalise_unicode(text)
    text = to_lowercase(text)
    text = remove_special_characters(text)
    text = collapse_whitespace(text)
    return text
