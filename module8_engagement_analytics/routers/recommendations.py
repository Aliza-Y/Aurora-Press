# routers/recommendations.py
from fastapi import APIRouter, HTTPException
from ..db.mongo import get_db

router = APIRouter()


@router.get("/recommendations/{article_id}")
def get_recommendations(article_id: str):
    db = get_db()
    doc = db["recommendations"].find_one({"article_id": article_id}, sort=[("generated_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No recommendations yet")
    doc["_id"] = str(doc["_id"])
    return doc
