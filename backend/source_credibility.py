# source_credibility.py
# Verifies the credibility of news sources using a known-reliable domains list
# and optionally fetches domain reputation via the News API.

import re
from urllib.parse import urlparse
from typing import Optional

import httpx  # pip install httpx

# ---------------------------------------------------------------------------
# Curated source credibility tiers
# ---------------------------------------------------------------------------
TRUSTED_SOURCES = {
    # Tier 1 — High credibility (score: 85-100)
    "tier1": {
        "score": 90,
        "label": "Highly Credible",
        "domains": [
            "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
            "thehindu.com", "ndtv.com", "hindustantimes.com",
            "timesofindia.indiatimes.com", "indianexpress.com",
            "pib.gov.in", "newsonair.gov.in",
            "theguardian.com", "nytimes.com", "washingtonpost.com",
            "economist.com", "ft.com",
        ],
    },
    # Tier 2 — Generally reliable (score: 60-84)
    "tier2": {
        "score": 70,
        "label": "Generally Reliable",
        "domains": [
            "scroll.in", "thewire.in", "firstpost.com", "livemint.com",
            "deccanherald.com", "telegraphindia.com", "outlookindia.com",
            "businessstandard.com", "financialexpress.com",
            "abcnews.go.com", "nbcnews.com", "cnn.com", "aljazeera.com",
        ],
    },
    # Tier 3 — Satire / Parody (score: 10)
    "satire": {
        "score": 10,
        "label": "Satire / Parody",
        "domains": [
            "theonion.com", "thebabylonbee.com", "faking-news.in",
        ],
    },
    # Known unreliable / misinformation sources (score: 5)
    "unreliable": {
        "score": 5,
        "label": "Known Misinformation Source",
        "domains": [
            "postcard.news", "sudarshannews.in",
        ],
    },
}

# Build flat lookup: domain → (score, label, tier)
_DOMAIN_LOOKUP: dict = {}
for tier_key, tier_data in TRUSTED_SOURCES.items():
    for domain in tier_data["domains"]:
        _DOMAIN_LOOKUP[domain] = {
            "score": tier_data["score"],
            "label": tier_data["label"],
            "tier": tier_key,
        }


def _extract_domain(url: str) -> str:
    """Extract root domain from a URL string."""
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        host = parsed.netloc or parsed.path
        # Remove www.
        host = re.sub(r"^www\.", "", host)
        return host.lower().strip()
    except Exception:
        return url.lower().strip()


def check_source_credibility(url_or_domain: str) -> dict:
    """
    Look up the credibility of a news source by URL or domain.

    Returns a dict with:
        - credibility_score (0-100)
        - label: human-readable tier label
        - tier: internal tier key
        - domain: cleaned domain string
        - verified_alternatives: list of trusted domains to suggest
        - is_known: whether the domain is in our database
    """
    domain = _extract_domain(url_or_domain)

    # Try exact match first, then check if domain ends with a known domain
    info = _DOMAIN_LOOKUP.get(domain)
    if not info:
        for known_domain, known_info in _DOMAIN_LOOKUP.items():
            if domain.endswith(known_domain):
                info = known_info
                break

    if info:
        score = info["score"]
        label = info["label"]
        tier = info["tier"]
        is_known = True
    else:
        # Unknown domain — assign neutral score
        score = 40
        label = "Unknown Source"
        tier = "unknown"
        is_known = False

    # Suggest verified alternatives (always suggest top Tier 1 sources)
    verified_alternatives = [
        {"domain": d, "label": TRUSTED_SOURCES["tier1"]["label"]}
        for d in TRUSTED_SOURCES["tier1"]["domains"][:5]
    ]

    return {
        "domain": domain,
        "credibility_score": score,
        "label": label,
        "tier": tier,
        "is_known": is_known,
        "verified_alternatives": verified_alternatives,
    }


async def fetch_related_verified_articles(query: str, news_api_key: str) -> list:
    """
    Optional: Fetch related verified articles from NewsAPI.org.
    Returns a list of article dicts from trusted sources only.

    Args:
        query: search keywords extracted from the article
        news_api_key: your NewsAPI key (set in .env as NEWS_API_KEY)
    """
    if not news_api_key:
        return []

    trusted_domains = ",".join(TRUSTED_SOURCES["tier1"]["domains"][:5])
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={query}&domains={trusted_domains}&pageSize=3"
        f"&apiKey={news_api_key}"
    )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            data = response.json()
            articles = data.get("articles", [])
            return [
                {
                    "title": a.get("title"),
                    "url": a.get("url"),
                    "source": a.get("source", {}).get("name"),
                    "published_at": a.get("publishedAt"),
                }
                for a in articles
            ]
    except Exception:
        return []