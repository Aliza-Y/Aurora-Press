# routers/articles.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from ..db.mongo import get_db
from fastapi import Depends
from module8_engagement_analytics.dependencies.auth import require_api_key

API_KEY = None  # optionally set via env later

router = APIRouter()

class ArticleIn(BaseModel):
    article_id: str
    title: str
    abstract: Optional[str] = ""
    category: str
    subcategory: Optional[str] = ""
    url: str
    platforms: List[str] = ["site"]
    published_at: Optional[datetime] = None


@router.post("/register-article", dependencies=[Depends(require_api_key)])
def register_article(a: ArticleIn):
    try:
        if API_KEY and x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
        db = get_db()
        doc = a.dict()
        if doc["published_at"] is None:
            doc["published_at"] = datetime.now(timezone.utc)
        db["published_articles"].update_one({"article_id": a.article_id},
                                            {"$set": doc}, upsert=True)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
