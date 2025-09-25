# module8_engagement_analytics/db/mongo.py
import os
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database

MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("DB_NAME", "aurorapress")

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(
            MONGO_URL,
            serverSelectionTimeoutMS=2000,  # 2s instead of 30+ seconds
            connectTimeoutMS=2000,
            socketTimeoutMS=2000,
        )
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db: Database) -> None:
    ev: Collection = db["article_events"]

    # Common query helpers
    ev.create_index([("article_id", ASCENDING)])
    ev.create_index([("event_type", ASCENDING)])
    ev.create_index([("category", ASCENDING)])
    ev.create_index([("platform", ASCENDING)])
    # ⚠️ DO NOT also create a plain timestamp index; TTL will cover it.

    # Create a TTL index with a distinct name so it never clashes with a plain index
    TTL_NAME = "timestamp_ttl_90d"
    TTL_SECONDS = 60 * 60 * 24 * 90

    # If an old plain index existed, user should have dropped it (step 1).
    # Here we create TTL if it's missing; if it exists with wrong options we can recreate.
    existing = {idx["name"]: idx for idx in ev.list_indexes()}
    if TTL_NAME not in existing:
        try:
            ev.create_index([("timestamp", ASCENDING)],
                            name=TTL_NAME,
                            expireAfterSeconds=TTL_SECONDS)
        except Exception as e:
            # Last resort: if some other timestamp index still blocks, ignore or log.
            print(f"[WARN] TTL index create failed: {e}")

    # Published articles indexes
    pa: Collection = db["published_articles"]
    pa.create_index([("article_id", ASCENDING)], unique=True)
    pa.create_index([("published_at", ASCENDING)])
