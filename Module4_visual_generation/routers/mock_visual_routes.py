from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import base64
import json

router = APIRouter()

class MockImageData(BaseModel):
    image_id: str
    image_type: str
    image_data: str
    caption: str
    style: str

class MockVisualGenerationRequest(BaseModel):
    article_title: str
    article_content: str
    article_summary: str
    category: str
    keywords: List[str]
    max_images: int = 2

class MockVisualGenerationResponse(BaseModel):
    success: bool
    images: List[MockImageData]
    message: str
    total_images: int
    generation_time: float

@router.post("/generate-simple", response_model=MockVisualGenerationResponse)
async def generate_simple_visuals(request: MockVisualGenerationRequest):
    """
    Mock visual generation endpoint that returns placeholder images
    """
    try:
        # Create mock images based on category
        images = []
        
        # Generate header image
        header_caption = f"Header image for: {request.article_title}"
        header_image = create_mock_image(request.category, "header")
        
        images.append(MockImageData(
            image_id=f"header_{request.category}_{len(images)}",
            image_data=header_image,
            caption=header_caption,
            image_type="header",
            style="realistic" if request.category in ["politics", "business", "technology", "science"] else "artistic"
        ))
        
        # Generate inline image if max_images > 1
        if request.max_images > 1:
            inline_caption = f"Related to: {', '.join(request.keywords[:3])}"
            inline_image = create_mock_image(request.category, "inline")
            
            images.append(MockImageData(
                image_id=f"inline_{request.category}_{len(images)}",
                image_data=inline_image,
                caption=inline_caption,
                image_type="inline",
                style="realistic" if request.category in ["politics", "business", "technology", "science"] else "artistic"
            ))
        
        return MockVisualGenerationResponse(
            success=True,
            images=images,
            message=f"Generated {len(images)} mock images for {request.category} article",
            total_images=len(images),
            generation_time=0.5  # Mock generation time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock visual generation failed: {str(e)}")

def create_mock_image(category: str, image_type: str) -> str:
    """
    Create a simple mock image as base64
    """
    # Create a simple SVG image based on category
    svg_content = f"""
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#1E293B"/>
        <text x="200" y="150" text-anchor="middle" fill="#2DD4BF" font-family="Arial" font-size="20">
            {category.upper()} {image_type.upper()}
        </text>
        <text x="200" y="180" text-anchor="middle" fill="#94A3B8" font-family="Arial" font-size="14">
            Mock Image
        </text>
    </svg>
    """
    
    # Convert SVG to base64
    svg_bytes = svg_content.encode('utf-8')
    base64_image = base64.b64encode(svg_bytes).decode('utf-8')
    
    return f"data:image/svg+xml;base64,{base64_image}"
