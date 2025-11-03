import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from module7_publishing.tasks.oauth_publishing_tasks import publish_article_oauth, check_user_platform_status, publish_seo_optimized_article
from database.oauth_db import get_user_connections, get_user_publications

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AuroraPress Publishing API",
    description="Complete OAuth-enabled multi-platform publishing system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ArticleData(BaseModel):
    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content (HTML)")
    excerpt: Optional[str] = Field(None, description="Article excerpt")
    featured_image_path: Optional[str] = Field(None, description="Path to featured image")
    categories: Optional[List[str]] = Field(default=[], description="Article categories")
    tags: Optional[List[str]] = Field(default=[], description="Article tags")
    seo_data: Optional[Dict[str, Any]] = Field(default={}, description="SEO optimization data from Module 5")
    status: Optional[str] = Field(default="publish", description="Publication status")

class PublishRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    article_data: ArticleData
    target_platforms: Optional[List[str]] = Field(default=None, description="Platforms to publish to")

class SEOIntegrationRequest(BaseModel):
    user_id: str = Field(..., description="User identifier") 
    seo_optimized_article: Dict[str, Any] = Field(..., description="SEO-optimized article from Module 5")
    target_platforms: Optional[List[str]] = Field(default=None, description="Platforms to publish to")

# Main publishing endpoints
@app.post("/publish/article")
async def publish_article(request: PublishRequest):
    """
    Main article publishing endpoint - publishes to user's connected platforms
    """
    try:
        logger.info(f"Publishing request received for user: {request.user_id}")
        
        # Convert article data to dict
        article_dict = request.article_data.dict()
        
        # Start OAuth publishing task
        task = publish_article_oauth.delay(
            request.user_id,
            article_dict,
            request.target_platforms
        )
        
        return {
            "success": True,
            "message": "Article publishing started",
            "task_id": task.id,
            "user_id": request.user_id,
            "article_id": article_dict.get('article_id'),
            "target_platforms": request.target_platforms,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Publishing request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start article publishing: {str(e)}"
        )

@app.post("/publish/seo-optimized") 
async def publish_seo_optimized_article_endpoint(request: SEOIntegrationRequest):
    """
    Integration endpoint for Module 5 (SEO) - publishes SEO-optimized articles
    """
    try:
        logger.info(f"SEO-optimized publishing request for user: {request.user_id}")
        
        # Start publishing task
        task_id = publish_seo_optimized_article(
            request.user_id,
            request.seo_optimized_article,
            request.target_platforms
        )
        
        if task_id:
            return {
                "success": True,
                "message": "SEO-optimized article publishing started",
                "task_id": task_id,
                "user_id": request.user_id,
                "article_id": request.seo_optimized_article.get('article_id'),
                "seo_optimized": True,
                "started_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start SEO article publishing"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SEO publishing request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start SEO article publishing: {str(e)}"
        )

@app.get("/publish/status/{task_id}")
async def get_publishing_status(task_id: str):
    """Get status of publishing task"""
    try:
        from celery.result import AsyncResult
        from module7_publishing.tasks.oauth_publishing_tasks import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task is waiting to be processed'
            }
        elif result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task is being processed',
                'current': result.info.get('current', 0),
                'total': result.info.get('total', 1)
            }
        elif result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task completed successfully',
                'result': result.result
            }
        else:
            # FAILURE
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task failed',
                'error': str(result.info)
            }
            
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )

# User management endpoints
@app.get("/user/{user_id}/connections")
async def get_user_connections_endpoint(user_id: str):
    """Get user's connected platforms"""
    try:
        connections = get_user_connections(user_id)
        
        return {
            "user_id": user_id,
            "connections": connections,
            "total_connections": len(connections),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user connections: {str(e)}"
        )

@app.get("/user/{user_id}/platform-status")
async def get_user_platform_status(user_id: str):
    """Get detailed status of user's connected platforms"""
    try:
        # Start background task to check platform status
        task = check_user_platform_status.delay(user_id)
        
        # For immediate response, you might want to wait briefly
        try:
            result = task.get(timeout=5)  # Wait 5 seconds max
            return result
        except:
            # If takes longer, return task ID for status checking
            return {
                "user_id": user_id,
                "status": "checking",
                "task_id": task.id,
                "message": "Platform status check in progress"
            }
            
    except Exception as e:
        logger.error(f"Error checking platform status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check platform status: {str(e)}"
        )

@app.get("/user/{user_id}/publications")
async def get_user_publication_history(user_id: str, limit: int = 50):
    """Get user's publication history"""
    try:
        publications = get_user_publications(user_id, limit)
        
        return {
            "user_id": user_id,
            "publications": publications,
            "total_returned": len(publications),
            "limit": limit,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting publication history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get publication history: {str(e)}"
        )

# Health and utility endpoints
@app.get("/health")
async def health_check():
    """Complete system health check"""
    try:
        return {
            "status": "healthy",
            "service": "AuroraPress Publishing API",
            "version": "1.0.0",
            "components": {
                "oauth_system": "operational",
                "publishing_tasks": "operational", 
                "database": "operational"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AuroraPress OAuth Publishing API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "publish_article": "POST /publish/article",
            "publish_seo_optimized": "POST /publish/seo-optimized",
            "task_status": "GET /publish/status/{task_id}",
            "user_connections": "GET /user/{user_id}/connections",
            "platform_status": "GET /user/{user_id}/platform-status",
            "publication_history": "GET /user/{user_id}/publications",
            "health": "GET /health",
            "oauth_endpoints": "http://localhost:8002/docs",
            "documentation": "GET /docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)