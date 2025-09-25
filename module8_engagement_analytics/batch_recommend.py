# module8_engagement_analytics/batch_recommend.py
import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pymongo import MongoClient

from services.recs import score_article, suggest_best_hours
from services.feedback import generate_feedback
from services.timeline import build_timeline

MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")
DB_NAME   = os.getenv("DB_NAME", "aurorapress")

BASE_DIR  = Path(__file__).resolve().parent
LOG_PATH  = BASE_DIR / "batch_recs.log"
HIST_PATH = BASE_DIR / "run_history.jsonl"   # <— new

def log_line(msg: str):
    now_utc = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{now_utc} UTC] {msg}\n")

def append_history(payload: dict):
    """Append one JSON line per run for later analysis."""
    with open(HIST_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, default=str) + "\n")

def aggregate_engagement(coll, article_id, since):
    cur = coll.aggregate([
        {"$match": {"article_id": article_id, "timestamp": {"$gte": since}}},
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
    ])
    out = {"view": 0, "share": 0}
    for r in cur:
        out[r["_id"]] = r["count"]
    return out

def main():
    started = datetime.now(timezone.utc)
    status = "ok"
    processed = 0
    error = None

    try:
        mc = MongoClient(MONGO_URL)
        db = mc[DB_NAME]
        arts   = db["published_articles"]
        events = db["article_events"]
        recs   = db["recommendations"]

        now = started
        start = now - timedelta(hours=24)
        end   = now - timedelta(hours=12)

        for a in arts.find({"published_at": {"$gte": start, "$lte": end}}):
            aid = a.get("article_id")
            if not aid:
                continue

            published_at = a.get("published_at", now - timedelta(hours=12))
            category     = a.get("category", "general")

            stats12h = aggregate_engagement(events, aid, published_at)
            timeline = build_timeline(events, aid, days=3, granularity="hour")

            top_hours = suggest_best_hours(category, top_k=3)
            dow = now.weekday()

            scored = []
            for item in top_hours:
                hour = int(item["hour"])
                s = score_article({
                    "title": a.get("title", ""),
                    "abstract": a.get("abstract", ""),
                    "category": category,
                    "subcategory": a.get("subcategory", ""),
                    "hour": hour,
                    "dow": dow
                }, w_model=0.7)
                scored.append({"hour": hour, **s})

            summary = generate_feedback(a, timeline, scored)

            rec_doc = {
                "article_id": aid,
                "window": "T+12h",
                "generated_at": now,
                "engagement_12h": stats12h,
                "timeline": timeline,
                "suggestions": scored,
                "summary": summary,
                "status": "ready"
            }

            db["recommendations"].update_one(
                {"article_id": aid, "window": "T+12h"},
                {"$set": rec_doc},
                upsert=True
            )
            processed += 1

        print("Batch recommendations completed.")
        log_line(f"Batch recommendations completed. processed={processed}")

    except Exception as e:
        status = "failed"
        error = str(e)
        msg = f"Batch recommendations FAILED: {error}"
        print(msg)
        log_line(msg)
        raise
    finally:
        finished = datetime.now(timezone.utc)
        append_history({
            "started_utc": started.isoformat(),
            "finished_utc": finished.isoformat(),
            "duration_seconds": (finished - started).total_seconds(),
            "status": status,
            "processed": processed,
            "error": error
        })

if __name__ == "__main__":
    main()
