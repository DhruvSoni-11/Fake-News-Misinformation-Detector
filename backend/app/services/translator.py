"""
app/services/translator.py
---------------------------
Optional multilingual support.

Strategy
────────
We use the `deep-translator` library (no API key required for Google backend)
to translate non-English text to English before the NLP pipeline runs.
Language detection is handled by `langdetect`.

Both libraries are *optional*.  If they are not installed the translate()
function transparently returns the original text and logs a warning, so the
rest of the pipeline keeps working (English-only).

Install extras:
    pip install deep-translator langdetect
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ── Optional imports ──────────────────────────────────────────────────────────

try:
    from langdetect import detect, LangDetectException  # type: ignore
    _LANGDETECT_AVAILABLE = True
except ImportError:
    _LANGDETECT_AVAILABLE = False
    logger.info("langdetect not installed — language detection disabled.")

try:
    from deep_translator import GoogleTranslator  # type: ignore
    _TRANSLATOR_AVAILABLE = True
except ImportError:
    _TRANSLATOR_AVAILABLE = False
    logger.info("deep-translator not installed — translation disabled.")


# ── Public API ────────────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """
    Detect the language of *text*.

    Returns a BCP-47 language code (e.g. "en", "fr", "ar") or "unknown"
    if detection fails or the library is unavailable.
    """
    if not _LANGDETECT_AVAILABLE:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def translate_to_english(text: str, source_lang: str = "auto") -> tuple[str, str]:
    """
    Translate *text* to English.

    Parameters
    ----------
    text:
        The input text in any language.
    source_lang:
        BCP-47 code of the source language, or ``"auto"`` (default) to let
        the translator detect it automatically.

    Returns
    -------
    tuple[str, str]
        ``(translated_text, detected_language)`` — the translated text and
        the detected source language code (``"en"`` if already English,
        ``"unknown"`` if detection failed).
    """
    detected = detect_language(text) if source_lang == "auto" else source_lang

    # Already English — skip translation
    if detected == "en":
        return text, "en"

    if not _TRANSLATOR_AVAILABLE:
        logger.warning(
            "deep-translator unavailable; returning original %s text untranslated.",
            detected,
        )
        return text, detected

    try:
        translated = GoogleTranslator(source=source_lang, target="en").translate(text)
        logger.info("Translated text from '%s' to 'en' (%d chars).", detected, len(text))
        return translated or text, detected
    except Exception as exc:
        logger.error("Translation failed: %s — returning original text.", exc)
        return text, detected
