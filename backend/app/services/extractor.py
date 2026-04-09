"""
app/services/extractor.py
--------------------------
Responsible for fetching and extracting the body text of a news article
from a given URL.

Strategy (in order of preference):
  1. Try newspaper3k — purpose-built for news articles, handles JS-light pages.
  2. Fall back to requests + BeautifulSoup for sites that newspaper3k can't parse.

Both paths return a plain string of article text.
"""

from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── newspaper3k helper ────────────────────────────────────────────────────────

def _extract_with_newspaper(url: str) -> str | None:
    """
    Attempt extraction using newspaper3k.
    Returns the article text, or None if the library is unavailable or fails.
    """
    try:
        from newspaper import Article  # type: ignore

        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        if text:
            logger.info("newspaper3k extracted %d chars from %s", len(text), url)
            return text
        logger.warning("newspaper3k returned empty text for %s", url)
        return None
    except ImportError:
        logger.warning("newspaper3k not installed; skipping.")
        return None
    except Exception as exc:
        logger.warning("newspaper3k failed for %s: %s", url, exc)
        return None


# ── BeautifulSoup fallback ────────────────────────────────────────────────────

def _extract_with_bs4(url: str) -> str:
    """
    Fetch the raw HTML and extract visible text using BeautifulSoup.
    Strips scripts, styles and navigation elements.
    Raises httpx.HTTPError on network failures.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; FakeNewsDetector/1.0; "
            "+https://github.com/fake-news-detector)"
        )
    }
    response = httpx.get(url, headers=headers, timeout=settings.URL_FETCH_TIMEOUT, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "iframe", "noscript"]):
        tag.decompose()

    # Prefer <article> body; fall back to <main>, then <body>
    content_tag = soup.find("article") or soup.find("main") or soup.find("body")
    if content_tag is None:
        return soup.get_text(separator=" ", strip=True)

    text = content_tag.get_text(separator=" ", strip=True)
    logger.info("BeautifulSoup extracted %d chars from %s", len(text), url)
    return text


# ── Public API ────────────────────────────────────────────────────────────────

async def extract_text_from_url(url: str) -> str:
    """
    Extract the article body text from *url*.

    Tries newspaper3k first (best quality) and falls back to the
    BeautifulSoup strategy if newspaper3k fails or is not installed.

    Parameters
    ----------
    url:
        A publicly accessible news article URL.

    Returns
    -------
    str
        The extracted article text (may still contain some noise;
        the text_cleaner pipeline handles further normalisation).

    Raises
    ------
    ValueError
        If neither strategy yields any content.
    RuntimeError
        On unrecoverable network errors.
    """
    # 1. newspaper3k
    text = _extract_with_newspaper(url)
    if text:
        return text

    # 2. BeautifulSoup fallback
    try:
        text = _extract_with_bs4(url)
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"HTTP {exc.response.status_code} fetching URL: {url}"
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Network error fetching URL '{url}': {exc}") from exc

    if not text.strip():
        raise ValueError(f"No extractable text found at URL: {url}")

    return text
