from fastapi import FastAPI
from routers.visual_routes import router as visual_router
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AuroraPress Module 4 - Visual Generation",
    description="Generates article-relevant images, infographics, and captions.",
    version="1.0.0"
)

app.include_router(visual_router, prefix="/m4", tags=["Visual Generation"])


@app.get("/health")
async def health_check():
    """Basic health check."""
    logger.info("Health check pinged.")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
