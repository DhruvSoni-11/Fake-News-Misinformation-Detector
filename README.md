# TruthScan — Fake News & Misinformation Detector

A full-stack web app + browser extension that analyzes news articles and social media posts in real time. It assigns a credibility score using NLP, flags emotional manipulation, identifies misinformation patterns, detects Hindi and 10 regional Indian languages, and suggests verified sources.

---

## Project Structure

```
├── backend/
│   ├── main.py                    ← FastAPI entry point (replace with missing_features version)
│   ├── language_utils.py          ← Hindi + 10 regional language support
│   ├── emotional_manipulation.py  ← Emotional manipulation & bias detection
│   ├── source_credibility.py      ← Source verification + verified source suggestions
│   ├── database.py                ← MongoDB Atlas storage (scores + history)
│   ├── requirements.txt           ← Python dependencies
│   └── .env                       ← Backend secrets (MongoDB URI, News API key)
├── browser-extension/
│   ├── manifest.json              ← Chrome Manifest V3
│   ├── content.js                 ← Extracts article text from any page
│   ├── background.js              ← Context menu + badge updates
│   ├── popup.html                 ← Extension popup UI
│   ├── popup.js                   ← Popup logic + backend calls
│   └── icons/                     ← icon16.png, icon48.png, icon128.png
├── public/
│   └── index.html
├── src/
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   ├── index.css
│   ├── hooks/
│   │   └── useHighlighting.js     ← Suspicious phrase highlighting hook
│   └── components/
│       ├── Header.js / Header.css
│       ├── Analyzer.js / Analyzer.css
│       ├── ResultCard.js / ResultCard.css
│       ├── CredibilityMeter.js / CredibilityMeter.css
│       ├── HighlightedText.js / HighlightedText.css
│       ├── AnalysisResult.jsx     ← (from missing_features)
│       └── AnalysisHistory.jsx    ← (from missing_features, needs MongoDB)
├── .env                           ← React env (REACT_APP_API_URL)
└── package.json
```

---

## Backend Setup

### Step 1 — Copy missing feature files into backend/

```bash
cp missing_features/backend/language_utils.py        backend/
cp missing_features/backend/emotional_manipulation.py backend/
cp missing_features/backend/source_credibility.py     backend/
cp missing_features/backend/database.py               backend/
cp missing_features/backend/main.py                   backend/   # replaces existing
```

### Step 2 — Create and activate a virtual environment (recommended)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
pip install deep-translator langdetect motor "pymongo[srv]" httpx
```

### Step 4 — Set up the .env file

Create `backend/.env` from the example:

```bash
cp missing_features/.env.example backend/.env
```

Then edit it and fill in:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/fakenews
NEWS_API_KEY=your_key_from_newsapi.org
```

- **MongoDB URI** — from MongoDB Atlas → Connect → Drivers
- **News API Key** — free registration at https://newsapi.org/register

### Step 5 — Plug in your ML model

In `backend/main.py`, find the stub and replace it with your actual model:

```python
def _get_fake_news_probability(english_text: str) -> float:
    # ---- Replace with your existing model logic ----
    # from model import predict
    # return predict(english_text)
    return 0.3   # ← remove this line
```

### Step 6 — Run the backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be available at: **http://127.0.0.1:8000/docs**

---

## Frontend Setup

### Step 1 — Install dependencies

```bash
# from project root
npm install
```

### Step 2 — Set the API URL

The `.env` file in the project root already contains:

```env
REACT_APP_API_URL=http://127.0.0.1:8000
```

Change this to your deployed backend URL when going live.

### Step 3 — Copy missing feature components (optional)

```bash
cp missing_features/src/hooks/useHighlighting.js       src/hooks/
cp missing_features/src/components/AnalysisResult.jsx  src/components/
cp missing_features/src/components/AnalysisHistory.jsx src/components/
```

### Step 4 — Start the frontend

```bash
npm start
```

Opens at **http://localhost:3000**

---

## Browser Extension Setup

### Step 1 — Copy extension files

```bash
cp -r missing_features/browser-extension/ browser-extension/
```

### Step 2 — Add icons

Create `browser-extension/icons/` and add:
- `icon16.png` (16×16)
- `icon48.png` (48×48)
- `icon128.png` (128×128)

Any PNG works for development — even a plain coloured square.

### Step 3 — Point to your backend

In both `browser-extension/content.js` and `browser-extension/popup.js`:

```js
const API_BASE = "http://localhost:8000";
// Change to deployed URL when going live:
// const API_BASE = "https://your-backend.onrender.com";
```

### Step 4 — Load in Chrome

1. Open `chrome://extensions`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `browser-extension/` folder

The extension icon will appear in the toolbar. Click it on any news page to analyze!

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Full analysis — score, manipulation, source, language |
| `GET`  | `/history` | Recent analyses from MongoDB (`?limit=20&skip=0`) |
| `GET`  | `/history/{id}` | Single analysis by ID |
| `GET`  | `/health` | Health check |

### Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "SHOCKING: सरकार छुपा रही है सच!", "url": "https://postcard.news/article"}'
```

Both `text` and `url` are optional — send either or both.

### Response

```json
{
  "credibility_score": 18,
  "manipulation_score": 72,
  "risk_level": "high",
  "language": {
    "language_code": "hi",
    "language_name": "Hindi",
    "is_indian_language": true
  },
  "source": {
    "domain": "postcard.news",
    "credibility_score": 5,
    "label": "Known Misinformation Source",
    "is_known": true
  },
  "verified_alternatives": [
    { "title": "Reuters report", "url": "https://reuters.com/...", "source": "Reuters" }
  ],
  "suspicious_phrases": [
    { "phrase": "SHOCKING", "start": 0, "end": 8 }
  ],
  "flags": {
    "urgency_keywords": 0,
    "extreme_language": 1
  },
  "sentiment": {
    "label": "negative",
    "confidence": 0.91
  },
  "analysis_id": "6650a1b2c3d4e5f678901234"
}
```

---

## Features

| Feature | Status |
|---------|--------|
| Text input analysis | ✅ |
| URL input analysis | ✅ |
| Credibility score (0–100) | ✅ |
| Manipulation score | ✅ |
| Sentiment analysis (label + polarity + subjectivity) | ✅ |
| Hindi & 10 regional Indian languages | ✅ via `language_utils.py` |
| Emotional manipulation detection | ✅ via `emotional_manipulation.py` |
| Source credibility check | ✅ via `source_credibility.py` |
| Verified source suggestions | ✅ via News API |
| Suspicious phrase highlighting | ✅ |
| MongoDB history storage | ✅ via `database.py` |
| Browser extension (Chrome) | ✅ |

---

## Running Both Together

```bash
# Terminal 1 — backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
npm start
```

---

## Troubleshooting

**"Failed to fetch" in the browser**
- Make sure the backend is running on port 8000
- Check that `REACT_APP_API_URL` in `.env` matches
- If CORS errors appear, verify `allow_origins=["*"]` is set in `main.py`

**MongoDB connection fails**
- Double-check the `MONGODB_URI` in `backend/.env`
- Make sure your IP is whitelisted in MongoDB Atlas → Network Access

**Language detection not working**
- Install `langdetect`: `pip install langdetect`
- Some short texts may not detect reliably — try longer input

**Browser extension not showing**
- Make sure Developer mode is enabled in `chrome://extensions`
- Check that icon files exist in `browser-extension/icons/`
