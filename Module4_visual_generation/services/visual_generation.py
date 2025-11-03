import time
import uuid
from typing import List, Dict, Any
from ..models.schemas import (
    VisualGenerationRequest, 
    VisualGenerationResponse, 
    GeneratedImage,
    ImageStyle,
    ImageType
)
from .image_generation import ImageGenerationService
from .captioning import CaptionGenerationService
from .validation import VisualValidationService
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VisualGenerationService:
    """Main service for coordinating visual generation."""
    
    def __init__(self):
        self.logger = logger
        self.image_service = ImageGenerationService()
        self.caption_service = CaptionGenerationService()
        self.validation_service = VisualValidationService()
    
    async def generate_visuals(self, request: VisualGenerationRequest) -> VisualGenerationResponse:
        """Generate visuals for an article."""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting visual generation for article: {request.article_title}")
            
            # Validate request
            validation_result = self.validation_service.validate_request(request)
            if not validation_result["is_valid"]:
                return VisualGenerationResponse(
                    success=False,
                    images=[],
                    total_images=0,
                    generation_time=time.time() - start_time,
                    error_message=f"Validation failed: {', '.join(validation_result['errors'])}"
                )
            
            # Log warnings if any
            if validation_result["warnings"]:
                for warning in validation_result["warnings"]:
                    self.logger.warning(warning)
            
            # Generate images
            generated_images = self.image_service.generate_images(
                article_title=request.article_title,
                article_content=request.article_content,
                article_summary=request.article_summary,
                category=request.category,
                keywords=request.keywords,
                max_images=request.max_images,
                preferred_style=request.preferred_style
            )
            
            if not generated_images:
                return VisualGenerationResponse(
                    success=False,
                    images=[],
                    total_images=0,
                    generation_time=time.time() - start_time,
                    error_message="No images were generated"
                )
            
            # Generate captions for all images
            self._generate_captions_for_images(generated_images, request)
            
            # Validate generated images
            validated_images = self._validate_generated_images(generated_images)
            
            generation_time = time.time() - start_time
            memory_usage = self.image_service.check_memory_usage()
            
            self.logger.info(f"Successfully generated {len(validated_images)} images in {generation_time:.2f}s")
            
            return VisualGenerationResponse(
                success=True,
                images=validated_images,
                total_images=len(validated_images),
                generation_time=generation_time,
                memory_usage=memory_usage
            )
            
        except Exception as e:
            self.logger.error(f"Error in visual generation: {str(e)}")
            return VisualGenerationResponse(
                success=False,
                images=[],
                total_images=0,
                generation_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _generate_captions_for_images(
        self, 
        images: List[GeneratedImage], 
        request: VisualGenerationRequest
    ) -> None:
        """Generate captions for all images."""
        try:
            for image in images:
                caption = self.caption_service.generate_caption(
                    article_title=request.article_title,
                    article_content=request.article_content,
                    image_style=image.style,
                    image_type=image.image_type,
                    keywords=request.keywords,
                    prompt_used=image.prompt_used
                )
                image.caption = caption
                
        except Exception as e:
            self.logger.error(f"Error generating captions: {str(e)}")
            # Set fallback captions
            for image in images:
                if not image.caption:
                    image.caption = f"Image related to {request.article_title}"
    
    def _validate_generated_images(self, images: List[GeneratedImage]) -> List[GeneratedImage]:
        """Validate generated images and filter out invalid ones."""
        validated_images = []
        
        for image in images:
            validation_result = self.validation_service.validate_generated_image(
                image.image_data, 
                image.caption
            )
            
            if validation_result["is_valid"]:
                validated_images.append(image)
            else:
                self.logger.warning(f"Image {image.image_id} failed validation: {validation_result['errors']}")
        
        return validated_images
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'image_service'):
            self.image_service.cleanup()
        self.logger.info("Visual generation service cleaned up")
