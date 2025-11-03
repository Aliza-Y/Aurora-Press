# ============================================
# 🚀 AuroraPress Module 5 - SEO Optimization
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.seo_routes import router
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AuroraPress Module 5 - SEO Optimization",
    description="SEO optimization service for AuroraPress articles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "AuroraPress Module 5 - SEO Optimization",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)





