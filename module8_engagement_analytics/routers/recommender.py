# module8_engagement_analytics/routers/recommender.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from module8_engagement_analytics.db.mongo import get_db
from module8_engagement_analytics.services.timeline import build_timeline
from module8_engagement_analytics.services.recs import score_article, suggest_best_hours
from module8_engagement_analytics.services.feedback import generate_feedback

router = APIRouter()


# ---------- Existing: score a single article context ----------
class ScoreIn(BaseModel):
    title: str
    abstract: Optional[str] = ""
    category: str
    subcategory: Optional[str] = ""
    hour: int = Field(12, ge=0, le=23)
    dow: int = Field(2, ge=0, le=6)
    w_model: float = Field(0.7, ge=0.0, le=1.0)


@router.post("/score-article")
def api_score_article(data: ScoreIn):
    try:
        result = score_article(data.dict(), w_model=data.w_model)
        # also propose top hours for this category
        top_hours = suggest_best_hours(data.category, top_k=3)
        result["best_hours"] = top_hours
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Existing: best historical hours by priors ----------
@router.get("/best-hours/{category}")
def api_best_hours(category: str, k: int = 3):
    try:
        return {"category": category, "best_hours": suggest_best_hours(category, top_k=k)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- NEW: full recommendations for a published article ----------
@router.get("/recommendations/{article_id}")
def api_recommendations(
    article_id: str,
    days: int = Query(3, ge=1, le=14, description="How many days of history for the timeline"),
    granularity: str = Query("hour", pattern="^(hour|day)$"),
    k: int = Query(3, ge=1, le=8, description="How many future hours to suggest"),
    w_model: float = Query(0.7, ge=0.0, le=1.0, description="Blend weight for model vs time prior"),
):
    """
    Build a timeline from recent events, score top future hours, and return
    a human-readable editorial summary with suggestions.
    """
    try:
        db = get_db()
        arts = db["published_articles"]
        events = db["article_events"]

        art = arts.find_one({"article_id": article_id})
        if not art:
            raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")

        # 1) Build a recent timeline (hourly or daily)
        timeline = build_timeline(events, article_id, days=days, granularity=granularity)

        # 2) Rank candidate future hours by priors
        category = art.get("category", "General")
        top_hours = suggest_best_hours(category, top_k=k)

        # 3) Score those hours with your trained model
        dow = datetime.utcnow().weekday()
        suggestions = []
        for item in top_hours:
            h = int(item["hour"])
            scored = score_article(
                {
                    "title": art.get("title", ""),
                    "abstract": art.get("abstract", ""),
                    "category": category,
                    "subcategory": art.get("subcategory", ""),
                    "hour": h,
                    "dow": dow,
                },
                w_model=w_model,
            )
            suggestions.append({"hour": h, **scored})  # includes model_prob, time_prior, final_score, best_threshold

        # 4) Editorial summary (LLM or rule-based, depending on your feedback.py)
        summary = generate_feedback(art, timeline, suggestions)

        # 5) Return a presentation-ready payload
        return {
            "article_id": article_id,
            "generated_at": datetime.utcnow().isoformat(),
            "history_days": days,
            "granularity": granularity,
            "timeline": timeline,       # list of {ts, views, shares}
            "suggestions": suggestions, # list of {hour, model_prob, time_prior, final_score, ...}
            "summary": summary,         # editorial assistant style
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
