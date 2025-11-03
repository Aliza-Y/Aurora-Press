import re
from typing import List, Dict, Any
from ..models.schemas import VisualGenerationRequest, ImageStyle
from ..utils.logger import get_logger

logger = get_logger(__name__)

class VisualValidationService:
    """Service for validating visual generation requests and content."""
    
    def __init__(self):
        self.logger = logger
    
    def validate_request(self, request: VisualGenerationRequest) -> Dict[str, Any]:
        """Validate the visual generation request."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": {}
        }
        
        # Validate required fields
        if not request.article_title or len(request.article_title.strip()) < 5:
            validation_result["errors"].append("Article title must be at least 5 characters long")
            validation_result["is_valid"] = False
        
        if not request.article_content or len(request.article_content.strip()) < 50:
            validation_result["errors"].append("Article content must be at least 50 characters long")
            validation_result["is_valid"] = False
        
        if not request.keywords or len(request.keywords) == 0:
            validation_result["warnings"].append("No keywords provided, may affect image relevance")
        
        # Validate max_images
        if request.max_images > 2:
            validation_result["warnings"].append("Max images limited to 2 for memory efficiency")
            request.max_images = 2
        
        # Determine appropriate style based on category
        recommended_style = self._recommend_style(request.category)
        if not request.preferred_style:
            request.preferred_style = recommended_style
            validation_result["recommendations"]["style"] = f"Recommended style: {recommended_style.value}"
        
        # Check for potentially problematic content
        problematic_content = self._check_content_safety(request.article_content)
        if problematic_content:
            validation_result["warnings"].extend(problematic_content)
        
        return validation_result
    
    def _recommend_style(self, category: str) -> ImageStyle:
        """Recommend image style based on article category."""
        artistic_categories = ["entertainment", "health", "sports", "lifestyle", "arts"]
        
        if category.lower() in artistic_categories:
            return ImageStyle.ARTISTIC
        else:
            return ImageStyle.REALISTIC
    
    def _check_content_safety(self, content: str) -> List[str]:
        """Check content for potentially problematic themes."""
        warnings = []
        
        # Simple keyword-based safety check
        sensitive_keywords = [
            "violence", "war", "conflict", "attack", "death", "killing",
            "drug", "alcohol", "gambling", "porn", "adult"
        ]
        
        content_lower = content.lower()
        found_keywords = [kw for kw in sensitive_keywords if kw in content_lower]
        
        if found_keywords:
            warnings.append(f"Content contains sensitive themes: {', '.join(found_keywords)}")
        
        return warnings
    
    def validate_generated_image(self, image_data: str, caption: str) -> Dict[str, Any]:
        """Validate a generated image and its caption."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if image data is valid base64
        try:
            import base64
            base64.b64decode(image_data)
        except Exception:
            validation_result["errors"].append("Invalid base64 image data")
            validation_result["is_valid"] = False
        
        # Validate caption
        if not caption or len(caption.strip()) < 10:
            validation_result["warnings"].append("Caption is too short or empty")
        
        if len(caption) > 200:
            validation_result["warnings"].append("Caption is very long")
        
        return validation_result
