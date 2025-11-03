import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import module9_interview_ai.agents  # ✅ force registration
from module9_interview_ai.router import router as m9_router

# Try to import Module 4, but fallback to mock if not available
try:
    from Module4_visual_generation.routers.visual_routes import router as m4_router
    MODULE4_AVAILABLE = True
    print("✅ Module 4 (Visual Generation) loaded successfully")
except Exception as e:
    print(f"⚠️  Module 4 (Visual Generation) not available: {e}")
    print("🔄 Falling back to mock visual generation service...")
    try:
        from Module4_visual_generation.routers.mock_visual_routes import router as m4_router
        MODULE4_AVAILABLE = True
        print("✅ Mock Module 4 (Visual Generation) loaded successfully")
    except Exception as mock_e:
        print(f"❌ Mock Module 4 also failed: {mock_e}")
        MODULE4_AVAILABLE = False
        m4_router = None

# Try to import Module 5 (SEO Optimization)
try:
    from module5_seo.routers.seo_routes import router as m5_router
    MODULE5_AVAILABLE = True
    print("✅ Module 5 (SEO Optimization) loaded successfully")
except Exception as e:
    print(f"⚠️  Module 5 (SEO Optimization) not available: {e}")
    MODULE5_AVAILABLE = False
    m5_router = None

# Try to import Module 7 (Publishing & Distribution)
try:
    from module7_publishing.api.main_publishing_api import app as m7_app
    # OAuth endpoints are functions, not a separate app
    MODULE7_AVAILABLE = True
    print("✅ Module 7 (Publishing & Distribution) loaded successfully")
except Exception as e:
    print(f"⚠️  Module 7 (Publishing & Distribution) not available: {e}")
    MODULE7_AVAILABLE = False
    m7_app = None

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

# Import Module 7 integration helper
try:
    from module7_integration import (
        is_module7_available,
        publish_article_to_platforms,
        get_user_publishing_status,
        check_publishing_task_status,
        get_module7_info
    )
    MODULE7_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Module 7 integration helper not available: {e}")
    MODULE7_INTEGRATION_AVAILABLE = False

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
app = FastAPI(title="AuroraPress API")
app.include_router(m9_router)

# Include Module 4 router only if available
if MODULE4_AVAILABLE and m4_router:
    app.include_router(m4_router, prefix="/m4", tags=["Visual Generation"])
    print("✅ Module 4 routes registered")
else:
    print("⚠️  Module 4 routes not registered - visual generation will be disabled")

# Include Module 5 router only if available
if MODULE5_AVAILABLE and m5_router:
    app.include_router(m5_router, prefix="/m5", tags=["SEO Optimization"])
    print("✅ Module 5 routes registered")
else:
    print("⚠️  Module 5 routes not registered - SEO optimization will be disabled")

# Include Module 7 routers only if available
if MODULE7_AVAILABLE and m7_app:
    # Mount Module 7 publishing API as sub-application
    app.mount("/m7", m7_app, name="Module 7 Publishing")
    print("✅ Module 7 routes registered")
else:
    print("⚠️  Module 7 routes not registered - publishing will be disabled")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
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


# Module 7 Publishing Endpoints (if available)
if MODULE7_INTEGRATION_AVAILABLE:
    
    @app.get("/api/publishing/info")
    async def get_publishing_info():
        """Get Module 7 publishing information and status"""
        return get_module7_info()
    
    @app.post("/api/publishing/publish/{article_id}")
    async def publish_article_endpoint(article_id: str, user_id: str = "default_user", target_platforms: list = None):
        """Publish an article to connected platforms"""
        try:
            # Get the article first
            article = get_article(article_id)
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            # Publish the article
            result = publish_article_to_platforms(article, user_id, target_platforms)
            if not result:
                raise HTTPException(status_code=500, detail="Failed to start publishing task")
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")
    
    @app.get("/api/publishing/user/{user_id}/status")
    async def get_user_publishing_status_endpoint(user_id: str):
        """Get user's publishing platform connections"""
        result = get_user_publishing_status(user_id)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to get publishing status")
        return result
    
    @app.get("/api/publishing/task/{task_id}/status")
    async def get_publishing_task_status_endpoint(task_id: str):
        """Get status of a publishing task"""
        result = check_publishing_task_status(task_id)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to get task status")
        return result

else:
    # Fallback endpoints when Module 7 is not available
    @app.get("/api/publishing/info")
    async def get_publishing_info_fallback():
        return {
            "available": False,
            "message": "Module 7 (Publishing) is not available",
            "status": "unavailable"
        }


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