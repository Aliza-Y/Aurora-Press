from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class ImageStyle(str, Enum):
    REALISTIC = "realistic"
    ARTISTIC = "artistic"

class ImageType(str, Enum):
    HEADER = "header"
    INLINE = "inline"

class VisualGenerationRequest(BaseModel):
    article_title: str
    article_content: str
    article_summary: str
    category: str
    keywords: List[str]
    max_images: int = 2
    preferred_style: Optional[ImageStyle] = None

class GeneratedImage(BaseModel):
    image_id: str
    image_type: ImageType
    image_data: str  # base64 encoded
    caption: str
    style: ImageStyle
    prompt_used: str
    generation_metadata: Dict[str, Any]

class VisualGenerationResponse(BaseModel):
    success: bool
    images: List[GeneratedImage]
    total_images: int
    generation_time: float
    memory_usage: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None









