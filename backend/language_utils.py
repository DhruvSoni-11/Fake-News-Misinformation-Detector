# language_utils.py
# Handles Hindi & regional Indian language detection and translation
# Integrates with Google Translate API (or a free fallback via deep_translator)

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "en": "English",
}


def detect_language(text: str) -> dict:
    """Detect the language of the input text."""
    try:
        lang_code = detect(text)
        lang_name = SUPPORTED_LANGUAGES.get(lang_code, f"Unknown ({lang_code})")
        return {
            "language_code": lang_code,
            "language_name": lang_name,
            "is_indian_language": lang_code in SUPPORTED_LANGUAGES and lang_code != "en",
        }
    except LangDetectException:
        return {"language_code": "unknown", "language_name": "Unknown", "is_indian_language": False}


def translate_to_english(text: str, source_lang: str = "auto") -> dict:
    """
    Translate text to English for ML model processing.
    Returns original text unchanged if already English.
    """
    if source_lang == "en":
        return {"translated_text": text, "was_translated": False, "source_language": "en"}

    try:
        translator = GoogleTranslator(source=source_lang, target="en")
        translated = translator.translate(text)
        return {
            "translated_text": translated,
            "was_translated": True,
            "source_language": source_lang,
        }
    except Exception as e:
        # Fallback: return original text so pipeline doesn't break
        return {
            "translated_text": text,
            "was_translated": False,
            "source_language": source_lang,
            "error": str(e),
        }


def process_multilingual_input(text: str) -> dict:
    """
    Full pipeline: detect language → translate if needed → return enriched payload.
    Use this before passing text to the ML model.
    """
    lang_info = detect_language(text)
    lang_code = lang_info["language_code"]

    if lang_code != "en":
        translation = translate_to_english(text, source_lang=lang_code)
        english_text = translation["translated_text"]
    else:
        english_text = text
        translation = {"was_translated": False, "source_language": "en"}

    return {
        "original_text": text,
        "english_text": english_text,
        "language_info": lang_info,
        "translation_info": translation,
    }