# module8_engagement_analytics/routers/tracker.py
from typing import Optional, Literal
from datetime import datetime
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from fastapi import Depends
from module8_engagement_analytics.dependencies.auth import require_api_key


# ✅ use ABSOLUTE import into the package
from module8_engagement_analytics.db.mongo import get_db

router = APIRouter()


# --------- Schemas ---------
class EventData(BaseModel):
    article_id: str
    event_type: Literal["view", "share", "like", "comment"]
    platform: Optional[Literal["website", "twitter", "facebook", "linkedin"]] = "website"
    category: Optional[str] = "general"
    referrer: Optional[str] = None
    device_type: Optional[Literal["mobile", "desktop", "tablet"]] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    # Optional explicit timestamp if caller sends one; otherwise we set it.
    timestamp: Optional[datetime] = None


# --------- Routes ---------
@router.post("/track-event", dependencies=[Depends(require_api_key)])
async def track_event(data: EventData, request: Request):
    """Log a single engagement event."""
    payload = data.dict()
    payload["timestamp"] = payload.get("timestamp") or datetime.utcnow()
    payload["ip_address"] = request.client.host
    payload["user_agent"] = request.headers.get("user-agent")

    db = get_db()
    db["article_events"].insert_one(payload)
    return {"msg": "Event logged"}


@router.get("/analytics/{article_id}")
def get_analytics(article_id: str):
    """Aggregate total counts per event_type for an article."""
    db = get_db()
    pipeline = [
        {"$match": {"article_id": article_id}},
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
    ]
    results = list(db["article_events"].aggregate(pipeline))
    return {"article_id": article_id, "analytics": results}


@router.get("/analytics/{article_id}/timeline")
def get_engagement_timeline(article_id: str):
    """Daily timeline of views/shares for an article."""
    db = get_db()
    pipeline = [
        {"$match": {"article_id": article_id}},
        {"$group": {
            "_id": {
                "event_type": "$event_type",
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
            },
            "count": {"$sum": 1}
        }},
        {"$group": {
            "_id": "$_id.date",
            "events": {"$push": {"type": "$_id.event_type", "count": "$count"}}
        }},
        {"$sort": {"_id": 1}}
    ]

    result = db["article_events"].aggregate(pipeline)
    timeline = []
    for day in result:
        day_entry = {"date": day["_id"], "views": 0, "shares": 0}
        for e in day["events"]:
            if e["type"] == "view":
                day_entry["views"] = e["count"]
            elif e["type"] == "share":
                day_entry["shares"] = e["count"]
        timeline.append(day_entry)

    return {"article_id": article_id, "timeline": timeline}


