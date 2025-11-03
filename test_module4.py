#!/usr/bin/env python3
"""
Test script for Module 4 - Visual Generation
"""
import sys
import os
import asyncio
from pathlib import Path

# Add Module 4 to path
module4_path = Path(__file__).parent / "Module4_visual_generation"
sys.path.insert(0, str(module4_path))

from models.schemas import VisualGenerationRequest, ImageStyle
from services.visual_generation import VisualGenerationService

async def test_visual_generation():
    """Test the visual generation service."""
    print("🎨 Testing Module 4 - Visual Generation")
    print("=" * 50)
    
    # Create test request
    test_request = VisualGenerationRequest(
        article_title="Breaking: AI Technology Advances in Healthcare",
        article_content="Recent developments in artificial intelligence have shown promising results in medical diagnosis and treatment planning. Researchers at leading institutions have developed new algorithms that can detect diseases with unprecedented accuracy.",
        article_summary="AI technology is revolutionizing healthcare with new diagnostic tools and treatment methods.",
        category="technology",
        keywords=["AI", "healthcare", "technology", "medical"],
        max_images=1,  # Start with 1 image for testing
        preferred_style=ImageStyle.REALISTIC
    )
    
    print(f"📝 Article Title: {test_request.article_title}")
    print(f"🏷️  Category: {test_request.category}")
    print(f"🔑 Keywords: {', '.join(test_request.keywords)}")
    print(f"🎨 Style: {test_request.preferred_style.value}")
    print(f"📊 Max Images: {test_request.max_images}")
    print("\n🚀 Starting visual generation...")
    
    try:
        # Initialize service
        visual_service = VisualGenerationService()
        
        # Generate visuals
        response = await visual_service.generate_visuals(test_request)
        
        if response.success:
            print(f"✅ Success! Generated {response.total_images} images")
            print(f"⏱️  Generation time: {response.generation_time:.2f} seconds")
            
            if response.memory_usage:
                print(f"💾 Memory usage: {response.memory_usage['percentage']:.1f}%")
            
            for i, image in enumerate(response.images):
                print(f"\n🖼️  Image {i+1}:")
                print(f"   Type: {image.image_type.value}")
                print(f"   Style: {image.style.value}")
                print(f"   Caption: {image.caption}")
                print(f"   Data size: {len(image.image_data)} characters")
        else:
            print(f"❌ Failed: {response.error_message}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'visual_service' in locals():
            visual_service.cleanup()

if __name__ == "__main__":
    asyncio.run(test_visual_generation())









