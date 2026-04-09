"""
app/api/routes.py
-----------------
All API endpoints for the Fake News & Misinformation Detector.

Endpoints
---------
GET  /health      → liveness probe
POST /analyze     → main analysis pipeline
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.models.schema import AnalyzeRequest, AnalyzeResponse, HealthResponse
from app.services.extractor import extract_text_from_url
from app.services.nlp_service import analyse
from app.services.scoring import calculate_score, classify
from app.services.translator import translate_to_english
from app.utils.text_cleaner import clean_text
from app.utils.helpers import truncate

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Health ─────────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    tags=["Meta"],
)
async def health_check() -> HealthResponse:
    """Return 200 OK when the service is up and running."""
    return HealthResponse(status="ok", version=settings.APP_VERSION)


# ── Main Analysis ──────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyse a news article for misinformation",
    tags=["Analysis"],
    status_code=status.HTTP_200_OK,
)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    Full misinformation-detection pipeline.

    1. **Input resolution** — extract text from the URL *or* use raw text.
    2. **Translation** — detect language; translate to English if necessary.
    3. **Cleaning** — strip HTML, normalise, lowercase.
    4. **NLP** — tokenise, remove stopwords, detect keywords, sentiment.
    5. **Scoring** — compute credibility score and label.
    6. **Response** — return structured JSON.

    At least one of ``text`` or ``url`` must be provided in the request body.
    """
    # ── Step 1: Resolve raw text ──────────────────────────────────────────────
    source: str

    if payload.url:
        logger.info("Fetching article from URL: %s", payload.url)
        try:
            raw_text = await extract_text_from_url(payload.url)
        except (RuntimeError, ValueError) as exc:
            logger.error("URL extraction failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        source = "url"
    else:
        raw_text = payload.text  # type: ignore[assignment]
        source = "text"

    # Guard: enforce max text length
    if len(raw_text) > settings.MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Input text exceeds maximum allowed length of "
                f"{settings.MAX_TEXT_LENGTH:,} characters."
            ),
        )

    logger.info(
        "Processing %s input — %d raw characters.", source, len(raw_text)
    )

    # ── Step 2: Translate to English (optional) ───────────────────────────────
    try:
        english_text, detected_lang = translate_to_english(raw_text)
        if detected_lang not in ("en", "unknown"):
            logger.info("Detected language '%s'; translated to English.", detected_lang)
    except Exception as exc:
        # Translation is optional — log and continue with original text
        logger.warning("Translation step failed (%s); continuing with original text.", exc)
        english_text = raw_text

    # ── Step 3: Clean ─────────────────────────────────────────────────────────
    cleaned = clean_text(english_text)

    if not cleaned.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No meaningful text could be extracted from the provided input.",
        )

    # ── Step 4: NLP ───────────────────────────────────────────────────────────
    nlp_result = analyse(cleaned)

    # ── Step 5: Score & label ─────────────────────────────────────────────────
    score = calculate_score(nlp_result)
    label = classify(score)

    logger.info(
        "Analysis complete — score: %.2f | label: %s | keywords: %s | sentiment: %s",
        score,
        label,
        nlp_result.keywords_detected or "none",
        nlp_result.sentiment_label,
    )

    # ── Step 6: Build response ────────────────────────────────────────────────
    return AnalyzeResponse(
        cleaned_text=cleaned,
        score=score,
        label=label,
        keywords_detected=nlp_result.keywords_detected,
        sentiment=nlp_result.sentiment_label,
        sentiment_polarity=nlp_result.sentiment_polarity,
        sentiment_subjectivity=nlp_result.sentiment_subjectivity,
        word_count=nlp_result.word_count,
        source=source,
    )
