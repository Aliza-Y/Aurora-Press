# module8_engagement_analytics/routers/ops.py
from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from module8_engagement_analytics.db.mongo import get_db

router = APIRouter()

@router.get("/ops/today")
def ops_today():
    """
    Quick 'action center' for the last 24h:
    - pulls recs from Mongo 'recommendations'
    - returns a concise list: article_id, summary, top_hour and quick engagement stats
    """
    db = get_db()
    recs = db["recommendations"]
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    docs = list(recs.find({"generated_at": {"$gte": since}}).sort("generated_at", -1))
    out = []
    for d in docs:
        out.append({
            "article_id": d.get("article_id"),
            "generated_at": d.get("generated_at"),
            "summary": d.get("summary", ""),
            "top_hour": (d.get("suggestions", [{}])[0].get("hour")
                         if d.get("suggestions") else None),
            "engagement_12h": d.get("engagement_12h", {}),
        })
    return {"actions": out, "count": len(out)}
