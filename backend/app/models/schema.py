"""
app/models/schema.py
--------------------
Pydantic request and response models.
Strict validation keeps bad data from ever reaching the business layer.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, field_validator, model_validator, HttpUrl, Field


# ── Request ───────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """
    Payload for POST /analyze.

    At least one of `text` or `url` must be provided.
    If both are provided the URL takes precedence.
    """

    text: Optional[str] = Field(
        default=None,
        description="Raw article text to analyse.",
        examples=["Scientists discover a shocking new treatment..."],
    )
    url: Optional[str] = Field(
        default=None,
        description="Public URL of a news article to fetch and analyse.",
        examples=["https://example.com/news/article-123"],
    )

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError("`text` must not be blank.")
        return v

    @model_validator(mode="after")
    def at_least_one_input(self) -> "AnalyzeRequest":
        if not self.text and not self.url:
            raise ValueError("Provide at least one of `text` or `url`.")
        return self


# ── Response ──────────────────────────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """
    Full analysis result returned by POST /analyze.
    """

    # The cleaned, normalised version of the article body
    cleaned_text: str = Field(description="Article text after cleaning and normalisation.")

    # Credibility score 0-100 (higher = more credible)
    score: float = Field(ge=0, le=100, description="Credibility score between 0 and 100.")

    # Human-readable verdict
    label: str = Field(description="Classification label: Fake | Suspicious | Likely Real.")

    # Indicator keywords found in the article
    keywords_detected: list[str] = Field(
        description="List of misinformation-indicator keywords detected."
    )

    # Overall sentiment of the article
    sentiment: str = Field(
        description="Sentiment polarity label: Very Negative | Negative | Neutral | Positive | Very Positive."
    )

    # Numeric sentiment polarity (-1 to 1) and subjectivity (0 to 1)
    sentiment_polarity: float = Field(description="TextBlob polarity score (-1 to 1).")
    sentiment_subjectivity: float = Field(description="TextBlob subjectivity score (0 to 1).")

    # Word count of the cleaned article
    word_count: int = Field(description="Number of words in the cleaned article.")

    # Source of the text that was analysed
    source: str = Field(description="'url' or 'text' — indicates which input was used.")

    class Config:
        json_schema_extra = {
            "example": {
                "cleaned_text": "scientists discover new treatment for cancer ...",
                "score": 72.5,
                "label": "Likely Real",
                "keywords_detected": ["shocking"],
                "sentiment": "Neutral",
                "sentiment_polarity": 0.05,
                "sentiment_subjectivity": 0.42,
                "word_count": 312,
                "source": "text",
            }
        }


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
