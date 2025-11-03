from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.visual_routes import router as visual_router
from .utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AuroraPress Module 4 - Visual Generation",
    description="Generates article-relevant images and captions.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
