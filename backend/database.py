# database.py
# MongoDB Atlas integration for storing credibility scores and analysis history.
# Install: pip install motor python-dotenv

import os
from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI", "")  # Set in your .env file
DB_NAME = os.getenv("MONGODB_DB_NAME", "fake_news_detector")

# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------
_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        if not MONGO_URI:
            raise RuntimeError(
                "MONGODB_URI is not set. Add it to your .env file.\n"
                "Example: MONGODB_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/"
            )
        _client = AsyncIOMotorClient(MONGO_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


# ---------------------------------------------------------------------------
# Analysis history — saves every analysis result
# ---------------------------------------------------------------------------
async def save_analysis(result: dict) -> str:
    """
    Save a full analysis result to the 'analyses' collection.

    Expected keys in result:
        input_text, url (optional), credibility_score, manipulation_score,
        risk_level, language_code, flags, sentiment, source_info, verified_sources
    
    Returns the inserted document ID as string.
    """
    db = get_db()
    doc = {
        **result,
        "created_at": datetime.utcnow(),
    }
    inserted = await db["analyses"].insert_one(doc)
    return str(inserted.inserted_id)


async def get_analysis_history(limit: int = 20, skip: int = 0) -> list:
    """Retrieve recent analysis history, newest first."""
    db = get_db()
    cursor = (
        db["analyses"]
        .find({}, {"_id": 1, "input_text": 1, "credibility_score": 1,
                   "risk_level": 1, "language_code": 1, "created_at": 1})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # serialize ObjectId
        results.append(doc)
    return results


async def get_analysis_by_id(analysis_id: str) -> Optional[dict]:
    """Retrieve a single analysis result by its MongoDB ID."""
    from bson import ObjectId

    db = get_db()
    doc = await db["analyses"].find_one({"_id": ObjectId(analysis_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ---------------------------------------------------------------------------
# Domain credibility cache — avoids repeated lookups for the same domain
# ---------------------------------------------------------------------------
async def cache_domain_score(domain: str, score: int, label: str) -> None:
    """Upsert a domain's credibility score into the cache collection."""
    db = get_db()
    await db["domain_cache"].update_one(
        {"domain": domain},
        {"$set": {"domain": domain, "score": score, "label": label,
                  "updated_at": datetime.utcnow()}},
        upsert=True,
    )


async def get_cached_domain_score(domain: str) -> Optional[dict]:
    """Return cached domain score if it exists."""
    db = get_db()
    doc = await db["domain_cache"].find_one({"domain": domain})
    if doc:
        doc.pop("_id", None)
    return doc


# ---------------------------------------------------------------------------
# Indexes — call once on startup to ensure efficient queries
# ---------------------------------------------------------------------------
async def ensure_indexes() -> None:
    db = get_db()
    await db["analyses"].create_index([("created_at", -1)])
    await db["domain_cache"].create_index([("domain", 1)], unique=True)