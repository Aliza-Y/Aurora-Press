import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from celery import current_app

from module7_publishing.tasks.oauth_publishing_tasks import (
    publish_to_wordpress, 
    publish_to_social_media, 
    publish_complete_workflow,
    update_wordpress_post,
    get_task_status,
    retry_failed_publication
)
from module7_publishing.database.publishing_db import PublishingDB
from module7_publishing.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AuroraPress Publishing API",
    description="Module 7 - AI-Powered Publishing, Distribution & Live Updates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = PublishingDB()

# Pydantic models for request/response validation
class ArticleData(BaseModel):
    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content (HTML)")
    excerpt: Optional[str] = Field(None, description="Article excerpt")
    featured_image_path: Optional[str] = Field(None, description="Path to featured image")
    categories: Optional[List[str]] = Field(default=[], description="Article categories")
    tags: Optional[List[str]] = Field(default=[], description="Article tags")
    seo_data: Optional[Dict[str, Any]] = Field(default={}, description="SEO optimization data")
    status: Optional[str] = Field(default="publish", description="Publication status")

class PublishRequest(BaseModel):
    article_data: ArticleData
    target_platforms: Optional[List[str]] = Field(default=["wordpress"], description="Platforms to publish to")
    schedule_for: Optional[datetime] = Field(None, description="Schedule publication for specific time")

class UpdateRequest(BaseModel):
    post_id: int = Field(..., description="WordPress post ID")
    updated_article_data: ArticleData
    reason: Optional[str] = Field(default="Content update", description="Reason for update")

class SocialMediaRequest(BaseModel):
    article_data: ArticleData
    platforms: Optional[List[str]] = Field(default=["twitter", "linkedin"], description="Social media platforms")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_completion: Optional[str] = None

class PublishResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check for the publishing service"""
    try:
        # Check Redis connection
        redis_status = current_app.control.inspect().stats()
        
        # Check database connection
        db_test = db.publications.find_one()  # Simple query test
        
        return {
            "status": "healthy",
            "service": "AuroraPress Publishing API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "redis": "connected" if redis_status else "disconnected",
                "mongodb": "connected",
                "celery": "running" if redis_status else "stopped"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

# Publishing endpoints
@app.post("/publish/wordpress", response_model=PublishResponse, tags=["Publishing"])
async def publish_article_to_wordpress(request: PublishRequest):
    """Publish article to WordPress"""
    try:
        # Convert Pydantic model to dict
        article_data = request.article_data.dict()
        
        # Start Celery task
        task = publish_to_wordpress.delay(article_data)
        
        logger.info(f"WordPress publication task started: {task.id}")
        
        return PublishResponse(
            success=True,
            task_id=task.id,
            message="WordPress publication started",
            details={
                "article_id": article_data.get("article_id"),
                "title": article_data.get("title"),
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting WordPress publication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start WordPress publication: {str(e)}"
        )

@app.post("/publish/social", response_model=PublishResponse, tags=["Publishing"])
async def publish_to_social_media_platforms(request: SocialMediaRequest):
    """Publish article to social media platforms"""
    try:
        article_data = request.article_data.dict()
        platforms = request.platforms
        
        # Start Celery task
        task = publish_to_social_media.delay(article_data, platforms)
        
        logger.info(f"Social media publication task started: {task.id} for platforms: {platforms}")
        
        return PublishResponse(
            success=True,
            task_id=task.id,
            message=f"Social media publication started for: {', '.join(platforms)}",
            details={
                "article_id": article_data.get("article_id"),
                "platforms": platforms,
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting social media publication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start social media publication: {str(e)}"
        )

@app.post("/publish/complete", response_model=PublishResponse, tags=["Publishing"])
async def publish_complete_workflow_endpoint(request: PublishRequest):
    """Execute complete publishing workflow (WordPress + Social Media)"""
    try:
        article_data = request.article_data.dict()
        target_platforms = request.target_platforms or ["wordpress", "twitter", "linkedin"]
        
        # Start complete workflow task
        task = publish_complete_workflow.delay(article_data, target_platforms)
        
        logger.info(f"Complete workflow task started: {task.id} for platforms: {target_platforms}")
        
        return PublishResponse(
            success=True,
            task_id=task.id,
            message=f"Complete publishing workflow started for: {', '.join(target_platforms)}",
            details={
                "article_id": article_data.get("article_id"),
                "target_platforms": target_platforms,
                "workflow_type": "complete_publishing",
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting complete workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start complete workflow: {str(e)}"
        )

@app.post("/publish/update-wordpress", response_model=PublishResponse, tags=["Publishing"])
async def update_wordpress_post_endpoint(request: UpdateRequest):
    """Update existing WordPress post"""
    try:
        updated_data = request.updated_article_data.dict()
        
        # Start update task
        task = update_wordpress_post.delay(request.post_id, updated_data, request.reason)
        
        logger.info(f"WordPress update task started: {task.id} for post: {request.post_id}")
        
        return PublishResponse(
            success=True,
            task_id=task.id,
            message=f"WordPress post update started for post ID: {request.post_id}",
            details={
                "post_id": request.post_id,
                "reason": request.reason,
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting WordPress update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start WordPress update: {str(e)}"
        )

# Task management endpoints
@app.get("/tasks/{task_id}/status", response_model=TaskResponse, tags=["Tasks"])
async def get_task_status_endpoint(task_id: str):
    """Get status of a publishing task"""
    try:
        task_status = get_task_status.delay(task_id)
        status_data = task_status.get(timeout=10)
        
        return TaskResponse(
            task_id=task_id,
            status=status_data.get("status", "UNKNOWN"),
            message=status_data.get("error", "Task completed successfully") if status_data.get("status") == "FAILURE" else "Task running or completed",
            estimated_completion=None  # Could be enhanced with time estimates
        )
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )

@app.post("/tasks/{task_id}/retry", response_model=PublishResponse, tags=["Tasks"])
async def retry_task_endpoint(task_id: str):
    """Retry a failed publishing task"""
    try:
        retry_result = retry_failed_publication.delay(task_id)
        result_data = retry_result.get(timeout=10)
        
        if result_data.get("success"):
            return PublishResponse(
                success=True,
                task_id=result_data.get("new_task_id"),
                message=f"Task retry initiated. Original: {task_id}, New: {result_data.get('new_task_id')}"
            )
        else:
            return PublishResponse(
                success=False,
                message=result_data.get("error", "Failed to retry task")
            )
            
    except Exception as e:
        logger.error(f"Error retrying task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}"
        )

# Publication records endpoints
@app.get("/publications/{article_id}", tags=["Records"])
async def get_publication_records(article_id: str):
    """Get all publication records for an article"""
    try:
        records = db.get_all_publications(article_id)
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No publication records found for article: {article_id}"
            )
        
        return {
            "article_id": article_id,
            "total_publications": len(records),
            "publications": records,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting publication records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get publication records: {str(e)}"
        )

@app.get("/publications/{article_id}/{platform}", tags=["Records"])
async def get_platform_publication_record(article_id: str, platform: str):
    """Get publication record for specific platform"""
    try:
        record = db.get_publication_record(article_id, platform)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {platform} publication record found for article: {article_id}"
            )
        
        return {
            "article_id": article_id,
            "platform": platform,
            "publication": record,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting platform publication record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform publication record: {str(e)}"
        )

# Analytics endpoints
@app.get("/analytics/overview", tags=["Analytics"])
async def get_publishing_analytics(days: int = 30):
    """Get publishing analytics overview"""
    try:
        analytics = db.get_publication_analytics(days)
        
        return {
            "analytics": analytics,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

@app.get("/analytics/workflows", tags=["Analytics"])
async def get_workflow_analytics(limit: int = 50):
    """Get workflow execution analytics"""
    try:
        workflows = db.get_workflow_records(limit=limit)
        
        # Calculate workflow statistics
        total_workflows = len(workflows)
        successful_workflows = sum(1 for w in workflows if w.get('results', {}).get('overall_success', False))
        
        workflow_stats = {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "success_rate": (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            "recent_workflows": workflows[:10],  # Most recent 10
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        return workflow_stats
        
    except Exception as e:
        logger.error(f"Error getting workflow analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow analytics: {str(e)}"
        )

# Platform status endpoints
@app.get("/platforms/status", tags=["Platforms"])
async def get_platform_status():
    """Get status of all configured publishing platforms"""
    try:
        # Import here to avoid circular imports
        from module7_publishing.publishers.social_oauth_client import SocialMediaManager
        
        # Check social media platforms
        social_manager = SocialMediaManager()
        social_status = social_manager.get_platform_status()
        
        # Check WordPress
        from module7_publishing.publishers.wordpress_oauth_client import WordPressPublisher
        try:
            wp = WordPressPublisher()
            wordpress_status = {
                "available": True,
                "connected": True,
                "last_checked": datetime.utcnow().isoformat()
            }
        except Exception as e:
            wordpress_status = {
                "available": False,
                "connected": False,
                "error": str(e),
                "last_checked": datetime.utcnow().isoformat()
            }
        
        platform_status = {
            "wordpress": wordpress_status,
            **social_status,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return platform_status
        
    except Exception as e:
        logger.error(f"Error getting platform status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform status: {str(e)}"
        )

# Utility endpoints
@app.post("/maintenance/cleanup", tags=["Maintenance"])
async def cleanup_old_records(days: int = 90):
    """Clean up old database records"""
    try:
        cleanup_stats = db.cleanup_old_records(days)
        
        return {
            "cleanup_completed": True,
            "statistics": cleanup_stats,
            "cleaned_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup records: {str(e)}"
        )

@app.get("/config/platforms", tags=["Configuration"])
async def get_platform_configuration():
    """Get current platform configuration status"""
    try:
        config_status = {
            "wordpress": {
                "configured": bool(settings.WORDPRESS_URL and settings.WORDPRESS_USERNAME),
                "url": settings.WORDPRESS_URL,
                "supports": ["posts", "pages", "media", "categories", "tags"]
            },
            "twitter": {
                "configured": bool(settings.TWITTER_BEARER_TOKEN or settings.TWITTER_API_KEY),
                "supports": ["tweets", "threads", "media"]
            },
            "linkedin": {
                "configured": bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_ACCESS_TOKEN),
                "supports": ["posts", "articles", "media"]
            },
            "last_checked": datetime.utcnow().isoformat()
        }
        
        return config_status
        
    except Exception as e:
        logger.error(f"Error getting platform configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform configuration: {str(e)}"
        )

@app.post("/integrate/from-seo", response_model=PublishResponse, tags=["Integration"])
async def publish_from_seo_module(request: PublishRequest):
    """
    Integration endpoint for Module 5 (SEO) to publish optimized articles
    This endpoint receives SEO-optimized articles and publishes them
    """
    try:
        logger.info(f"Received SEO-optimized article for publishing: {request.article_data.title}")
        
        # Validate that SEO data is present
        if not request.article_data.seo_data:
            logger.warning("Article received without SEO data - proceeding anyway")
        
        # Start complete workflow with all platforms
        article_data = request.article_data.dict()
        target_platforms = request.target_platforms or ["wordpress", "twitter", "linkedin"]
        
        task = publish_complete_workflow.delay(article_data, target_platforms)
        
        logger.info(f"SEO integration workflow started: {task.id}")
        
        return PublishResponse(
            success=True,
            task_id=task.id,
            message="SEO-optimized article publishing workflow started",
            details={
                "article_id": article_data.get("article_id"),
                "seo_optimized": True,
                "target_platforms": target_platforms,
                "integration_source": "module_5_seo",
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error in SEO integration endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish SEO-optimized article: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 AuroraPress Publishing API starting up...")
    
    # Verify configuration
    missing_config = settings.validate_settings()
    if missing_config:
        logger.warning(f"⚠️ Missing configuration: {', '.join(missing_config)}")
    
    logger.info("✅ AuroraPress Publishing API ready!")
    logger.info(f"📝 API Documentation: http://localhost:{settings.API_PORT}/docs")
    logger.info(f"🔄 Flower Monitoring: http://localhost:5555")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 AuroraPress Publishing API shutting down...")
    try:
        db.close()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "publishing_api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )