from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import json
from ..models.schemas import VisualGenerationRequest, VisualGenerationResponse
from ..services.visual_generation import VisualGenerationService
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize the visual generation service
visual_service = VisualGenerationService()

@router.post("/generate", response_model=VisualGenerationResponse)
async def generate_visuals(request: VisualGenerationRequest):
    """Generate visuals for an article."""
    try:
        logger.info(f"Received visual generation request for: {request.article_title}")
        
        # Generate visuals
        response = await visual_service.generate_visuals(request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error_message)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in visual generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-simple")
async def generate_visuals_simple(
    article_title: str,
    article_content: str,
    article_summary: str,
    category: str,
    keywords: List[str],
    max_images: int = 2
):
    """Simplified endpoint for visual generation."""
    try:
        # Create request object
        request = VisualGenerationRequest(
            article_title=article_title,
            article_content=article_content,
            article_summary=article_summary,
            category=category,
            keywords=keywords,
            max_images=max_images
        )
        
        # Generate visuals
        response = await visual_service.generate_visuals(request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error_message)
        
        # Convert to simple format for easier integration
        simple_response = {
            "success": response.success,
            "images": [
                {
                    "image_id": img.image_id,
                    "image_type": img.image_type.value,
                    "image_data": img.image_data,
                    "caption": img.caption,
                    "style": img.style.value
                }
                for img in response.images
            ],
            "total_images": response.total_images,
            "generation_time": response.generation_time
        }
        
        return simple_response
        
    except Exception as e:
        logger.error(f"Error in simple visual generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        memory_info = visual_service.image_service.check_memory_usage()
        return {
            "status": "healthy",
            "service": "visual_generation",
            "memory_usage": memory_info,
            "pipeline_initialized": visual_service.image_service.pipeline is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.post("/cleanup")
async def cleanup_resources(background_tasks: BackgroundTasks):
    """Clean up resources to free memory."""
    try:
        background_tasks.add_task(visual_service.cleanup)
        return {"message": "Cleanup initiated"}
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
