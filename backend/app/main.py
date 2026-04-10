# main.py  — drop-in replacement / addition for your existing FastAPI backend
# Wires together: multilingual support, emotional manipulation, source credibility, MongoDB

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from language_utils import process_multilingual_input
from emotional_manipulation import analyze_emotional_manipulation
from source_credibility import check_source_credibility, fetch_related_verified_articles
from database import save_analysis, get_analysis_history, get_analysis_by_id, ensure_indexes

app = FastAPI(title="Fake News & Misinformation Detector API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    try:
        await ensure_indexes()
    except Exception as e:
        print(f"[WARN] MongoDB not connected: {e}")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
from app.models.schema import AnalyzeRequest, AnalyzeResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _compute_credibility_score(
    fake_news_probability: float,
    manipulation_score: int,
    source_score: Optional[int],
) -> int:
    """
    Combine ML fake-news probability + manipulation + source scores
    into a final 0-100 credibility score.
    """
    # Base score from ML model (fake_news_probability = 0 means real, 1 = fake)
    ml_score = int((1 - fake_news_probability) * 100)

    # Weighted blend
    weights = {"ml": 0.5, "manipulation": 0.25, "source": 0.25}
    manipulation_credibility = 100 - manipulation_score

    if source_score is not None:
        final = (
            ml_score * weights["ml"]
            + manipulation_credibility * weights["manipulation"]
            + source_score * weights["source"]
        )
    else:
        # Redistribute source weight to ml if no source available
        final = ml_score * 0.65 + manipulation_credibility * 0.35

    return max(0, min(100, int(final)))


from textblob import TextBlob

FAKE_KEYWORDS = [
    "shocking", "breaking", "exclusive", "conspiracy", "hoax",
    "exposed", "secret", "they don't want you to know", "cover-up",
    "miracle", "banned", "censored", "wake up", "deep state"
]

def _get_fake_news_probability(english_text: str) -> float:
    """
    Derives a fake probability from keyword hits + TextBlob subjectivity.
    Returns a float 0.0 (real) to 1.0 (fake).
    """
    text_lower = english_text.lower()

    # Keyword score — each hit adds weight
    keyword_hits = sum(1 for kw in FAKE_KEYWORDS if kw in text_lower)
    keyword_score = min(keyword_hits / 5, 1.0)  # caps at 1.0 after 5 hits

    # Subjectivity score from TextBlob (0 = objective, 1 = very subjective)
    blob = TextBlob(english_text)
    subjectivity = blob.sentiment.subjectivity

    # Weighted combination
    fake_probability = (keyword_score * 0.6) + (subjectivity * 0.4)
    return round(min(fake_probability, 1.0), 3)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short to analyze.")

    # 1. Language detection + translation
    lang_data = process_multilingual_input(request.text)
    english_text = lang_data["english_text"]
    language_info = lang_data["language_info"]

    # 2. ML fake-news probability on English text
    fake_prob = _get_fake_news_probability(english_text)

    # 3. Emotional manipulation analysis
    manipulation_data = analyze_emotional_manipulation(request.text)

    # 4. Source credibility (only if URL provided)
    source_data = None
    verified_sources = []
    if request.url:
        source_data = check_source_credibility(request.url)
        # Fetch related verified articles from NewsAPI
        # Use first 5 words of text as search query
        query_words = english_text.split()[:5]
        query = " ".join(query_words)
        verified_sources = await fetch_related_verified_articles(query, NEWS_API_KEY)

    # 5. Final credibility score
    source_score = source_data["credibility_score"] if source_data else None
    credibility_score = _compute_credibility_score(fake_prob, manipulation_data["manipulation_score"], source_score)

    # 6. Persist to MongoDB
    result_doc = {
        "input_text": request.text[:500],  # store excerpt
        "url": request.url,
        "user_id": None,
        "credibility_score": credibility_score,
        "manipulation_score": manipulation_data["manipulation_score"],
        "risk_level": manipulation_data["risk_level"],
        "language_code": language_info.get("language_code"),
        "flags": manipulation_data["flags"],
        "sentiment": manipulation_data.get("sentiment"),
        "source_info": source_data,
    }
    try:
        analysis_id = await save_analysis(result_doc)
    except Exception:
        analysis_id = None  # don't fail if DB is down

    blob = TextBlob(lang_data["english_text"])
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity <= -0.6:   sentiment_label = "Very Negative"
    elif polarity <= -0.1: sentiment_label = "Negative"
    elif polarity <= 0.1:  sentiment_label = "Neutral"
    elif polarity <= 0.6:  sentiment_label = "Positive"
    else:                  sentiment_label = "Very Positive"

    if credibility_score >= 70:   verdict = "Likely Real"
    elif credibility_score >= 40: verdict = "Suspicious"
    else:                         verdict = "Fake"

    detected_keywords = [
        kw for kw in FAKE_KEYWORDS
        if kw in lang_data["english_text"].lower()
    ]

    return AnalyzeResponse(
        cleaned_text=lang_data["english_text"],
        score=float(credibility_score),
        label=verdict,
        keywords_detected=detected_keywords,
        sentiment=sentiment_label,
        sentiment_polarity=round(polarity, 3),
        sentiment_subjectivity=round(subjectivity, 3),
        word_count=len(lang_data["english_text"].split()),
        source="url" if request.url else "text",
    )


@app.get("/history")
async def history(limit: int = 20, skip: int = 0):
    """Return recent analysis history from MongoDB."""
    try:
        return await get_analysis_history(limit=limit, skip=skip)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


@app.get("/history/{analysis_id}")
async def history_detail(analysis_id: str):
    """Return a single analysis result by ID."""
    try:
        doc = await get_analysis_by_id(analysis_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Analysis not found.")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}