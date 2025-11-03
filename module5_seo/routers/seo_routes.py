# ============================================
# 🚀 AuroraPress Module 5 - SEO Routes
# ============================================

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Dict, Any
from ..models.schemas import SEOOptimizationRequest, SEOOptimizationResponse, SEOProgressUpdate
from ..services.seo_service import SEOService
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/m5", tags=["SEO Optimization"])

# Global SEO service instance
seo_service = SEOService()

@router.post("/optimize", response_model=SEOOptimizationResponse)
async def optimize_article_endpoint(request: SEOOptimizationRequest):
    """
    Optimize article for SEO
    """
    try:
        logger.info(f"Received SEO optimization request for: {request.article_title}")
        
        # Run optimization
        result = await seo_service.optimize_article_simple(
            title=request.article_title,
            content=request.article_content
        )
        
        if result.get("success", True):
            return SEOOptimizationResponse(
                success=True,
                original_title=result["original_title"],
                optimized_title=result["optimized_title"],
                meta_description=result["meta_description"],
                optimized_content=result["optimized_content"],
                keywords=result["keywords"],
                intent=result["intent"],
                readability=result["readability"],
                structure=result["structure"],
                seo_score=result["seo_score"],
                slug=result["slug"],
                optimized_at=result["optimized_at"],
                processing_time=result.get("processing_time", 0)
            )
        else:
            return SEOOptimizationResponse(
                success=False,
                original_title=request.article_title,
                optimized_title=request.article_title,
                meta_description="",
                optimized_content=request.article_content,
                keywords={"primary": [], "secondary": [], "long_tail": []},
                intent="informational",
                readability={"flesch": 0, "grade": 0, "gunning_fog": 0},
                structure={"paragraphs": 0, "avg_sentences_per_para": 0, "avg_sentence_length": 0},
                seo_score=0,
                slug="",
                optimized_at="",
                processing_time=0,
                error_message=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        logger.error(f"SEO optimization endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "AuroraPress Module 5 - SEO Optimization"}

@router.post("/optimize-stream")
async def optimize_article_stream(request: SEOOptimizationRequest):
    """
    Optimize article with real-time progress streaming
    """
    async def generate_progress():
        task_id = f"seo_{int(time.time())}"
        
        try:
            # Add progress callback
            progress_updates = []
            
            def progress_callback(update: SEOProgressUpdate):
                progress_updates.append(update)
            
            seo_service.add_progress_callback(task_id, progress_callback)
            
            # Start optimization
            optimization_task = asyncio.create_task(
                seo_service.optimize_article_with_progress(request, task_id)
            )
            
            # Stream progress updates
            while not optimization_task.done():
                if progress_updates:
                    update = progress_updates.pop(0)
                    yield f"data: {update.json()}\n\n"
                await asyncio.sleep(0.1)
            
            # Get final result
            result = await optimization_task
            
            # Send final result
            yield f"data: {result.json()}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming SEO optimization error: {e}")
            error_update = SEOProgressUpdate(
                step="error",
                progress=0,
                message=f"Error: {str(e)}",
                completed=True
            )
            yield f"data: {error_update.json()}\n\n"
        finally:
            seo_service.remove_progress_callback(task_id)
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )





