import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import module9_interview_ai.agents  # ✅ force registration
from module9_interview_ai.router import router as m9_router

from module2_trend_analysis.trend_api import (
    get_trends,
    get_trend_detail,
    approve_trend,
    get_articles,
    get_article,
    recommend_top_topics,
    CATEGORIES,
    delete_article
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
app = FastAPI(title="AuroraPress API")
app.include_router(m9_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")


# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to AuroraPress API"}


# Categories endpoint
@app.get("/api/categories")
async def get_categories():
    return {"categories": CATEGORIES}


# Include trend analysis endpoints
@app.get("/api/trends")
async def api_get_trends(category: str = None, limit: int = 20):
    return await get_trends(category, limit)


@app.get("/api/articles")
def api_get_articles(limit: int = 10, skip: int = 0):
    return get_articles(limit, skip)


@app.get("/api/recommended-topics")
def api_recommend_topics(limit: int = 10):
    return recommend_top_topics(limit)


@app.get("/api/articles/{article_id}")
def api_get_article(article_id: str):
    return get_article(article_id)


@app.get("/api/trends/{trend_id}")
async def api_get_trend_detail(trend_id: str):
    return await get_trend_detail(trend_id)


@app.post("/approve_trend/{trend_id}")
async def api_approve_trend(trend_id: str):
    return await approve_trend(trend_id)


@app.delete("/api/articles/{article_id}")
async def api_delete_article(article_id: str):
    return await delete_article(article_id)


# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 