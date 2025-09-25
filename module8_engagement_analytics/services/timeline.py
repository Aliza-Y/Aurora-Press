# module8_engagement_analytics/services/timeline.py
from datetime import datetime, timedelta, timezone
from typing import List, Literal, Dict
from pymongo.collection import Collection

Gran = Literal["hour", "day"]

def _pipeline(article_id: str, since: datetime, granularity: Gran):
    if granularity == "hour":
        # Mongo 5+: dateTrunc gives exact hour buckets
        return [
            {"$match": {"article_id": article_id, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": {
                    "bucket": { "$dateTrunc": { "date": "$timestamp", "unit": "hour" } },
                    "event_type": "$event_type"
                },
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.bucket",
                "events": { "$push": {"type": "$_id.event_type", "count": "$count"}}
            }},
            {"$sort": {"_id": 1}}
        ]
    else:  # "day"
        return [
            {"$match": {"article_id": article_id, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": {
                    "bucket": { "$dateTrunc": { "date": "$timestamp", "unit": "day" } },
                    "event_type": "$event_type"
                },
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.bucket",
                "events": { "$push": {"type": "$_id.event_type", "count": "$count"}}
            }},
            {"$sort": {"_id": 1}}
        ]

def build_timeline(
    events_coll: Collection,
    article_id: str,
    days: int = 3,
    granularity: Gran = "hour"
) -> List[Dict]:
    """
    Returns a list like:
      [{"ts": "2025-08-15T10:00:00Z", "views": 14, "shares": 3}, ...]
    Granularity: "hour" or "day".
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    pipe = _pipeline(article_id, since, granularity)

    out = []
    for row in events_coll.aggregate(pipe):
        ts = row["_id"]
        views = 0
        shares = 0
        for e in row["events"]:
            if e["type"] == "view":
                views = e["count"]
            elif e["type"] == "share":
                shares = e["count"]
        out.append({
            "ts": ts.isoformat(),
            "views": int(views),
            "shares": int(shares),
        })
    return out
