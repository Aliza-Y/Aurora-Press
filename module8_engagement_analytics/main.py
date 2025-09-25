# module8_engagement_analytics/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from module8_engagement_analytics.routers.tracker import router as tracker_router
from module8_engagement_analytics.routers.recommender import router as recs_router
from module8_engagement_analytics.routers.articles import router as articles_router
from module8_engagement_analytics.routers.recommendations import router as recs_view_router
from module8_engagement_analytics.routers.ops import router as ops_router  # optional ops dashboard

app = FastAPI(
    title="AuroraPress – Module 8: Engagement & Analytics",
    version="0.8.0",
    description=(
        "APIs to track article engagement, analyze timelines, score posting windows, "
        "and generate human‑readable recommendations."
    ),
    contact={"name": "AuroraPress Team"},
)

# CORS (dev-friendly: allow everything)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/", tags=["health"])
def root():
    return {"message": "Module 8 is working"}

# Register routers exactly once
app.include_router(tracker_router, tags=["engagement-tracking"])
app.include_router(articles_router, tags=["articles"])
app.include_router(recs_router, tags=["scoring-and-priors"])
app.include_router(recs_view_router, tags=["recommendations"])
app.include_router(ops_router, tags=["ops"])  # optional helper endpoints
