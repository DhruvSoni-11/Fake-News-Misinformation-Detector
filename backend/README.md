# 🔍 Fake News & Misinformation Detector — Backend API

A production-ready FastAPI backend that analyses news articles (raw text or URL) and returns a **credibility score**, **classification label**, **detected keywords**, and **sentiment** analysis.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory, CORS, lifespan hooks, logging
│   ├── api/
│   │   └── routes.py        # API endpoints: GET /health, POST /analyze
│   ├── core/
│   │   ├── config.py        # Pydantic-settings configuration (env-overridable)
│   │   └── constants.py     # Keywords, scoring weights, classification thresholds
│   ├── models/
│   │   └── schema.py        # Pydantic request/response models
│   ├── services/
│   │   ├── extractor.py     # URL → article text (newspaper4k + BS4 fallback)
│   │   ├── nlp_service.py   # Tokenisation, stopwords, keyword detection, sentiment
│   │   ├── scoring.py       # Rule-based credibility scoring engine
│   │   └── translator.py    # Optional multilingual support (deep-translator)
│   └── utils/
│       ├── text_cleaner.py  # HTML stripping, normalisation, cleaning pipeline
│       └── helpers.py       # Generic utilities: clamp, truncate, timer decorator
├── requirements.txt
├── run.py                   # Dev server entry point
└── .env.example             # Environment variable template
```

---

## ⚡ Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure (optional)

```bash
cp .env.example .env
# Edit .env as needed
```

### 3. Run

```bash
python run.py
# or
uvicorn app.main:app --reload
```

Server starts at **http://localhost:8000**

Interactive API docs: **http://localhost:8000/docs**

---

## 📡 API Reference

### `GET /api/v1/health`

Liveness probe.

**Response**
```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `POST /api/v1/analyze`

Analyse a news article for misinformation.

**Request body** — at least one of `text` or `url` required:
```json
{
  "text": "SHOCKING conspiracy exposed — the deep state is hiding the truth!",
  "url": "https://example.com/news/article"
}
```
> When both are provided, `url` takes precedence.

**Response**
```json
{
  "cleaned_text": "shocking conspiracy exposed the deep state is hiding the truth",
  "score": 28.0,
  "label": "Fake",
  "keywords_detected": ["shocking", "conspiracy", "deep state"],
  "sentiment": "Negative",
  "sentiment_polarity": -0.42,
  "sentiment_subjectivity": 0.75,
  "word_count": 12,
  "source": "text"
}
```

**Labels**

| Label | Score range | Meaning |
|-------|-------------|---------|
| `Likely Real` | ≥ 65 | Article shows no significant red flags |
| `Suspicious` | 40 – 64 | Multiple indicators of low credibility |
| `Fake` | < 40 | Strong signals of misinformation |

---

## ⚙️ Scoring System

Starting from a base of **100**, the engine applies:

| Component | Effect |
|-----------|--------|
| High-risk keyword (e.g. "conspiracy", "deep state") | −6 pts each (cap −40) |
| Medium-risk keyword (e.g. "viral", "bombshell") | −3 pts each (cap −20) |
| Low-risk keyword (e.g. "allegedly", "reportedly") | −1.5 pts each (cap −10) |
| Very negative sentiment | −10 pts |
| Negative sentiment | −5 pts |
| Neutral sentiment | +5 pts |
| Mildly positive sentiment | +2 pts |
| Very positive sentiment (hype signal) | −3 pts |
| Article ≥ 600 words | +5 pts |
| Article 200–600 words | +2 pts |
| Article < 50 words | −5 pts |
| High word repetition (>5%) | −8 pts |
| Medium repetition (3–5%) | −4 pts |

All weights and thresholds are in `app/core/constants.py`.

---

## 🌐 Optional: Multilingual Support

Install extra packages to enable automatic translation to English before analysis:

```bash
pip install deep-translator langdetect
```

The `translator.py` service will automatically detect language and translate non-English articles. Without these packages the service degrades gracefully (English-only mode).

---

## 🏭 Production Deployment

```bash
# Multiple workers with gunicorn + uvicorn workers
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🧪 Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```
