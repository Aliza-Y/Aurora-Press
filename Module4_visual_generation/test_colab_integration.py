#!/usr/bin/env python3
"""
🚀 AuroraPress Module 4 - Colab Integration Test Script
Tests the connection and image generation with Google Colab
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Module4_visual_generation.services.colab_service import ColabService
from Module4_visual_generation.colab_config import colab_config

async def test_colab_connection():
    """Test if Colab endpoint is reachable"""
    print("🔍 Testing Colab connection...")
    print(f"   Endpoint: {colab_config.COLAB_API_URL}")
    
    async with ColabService() as colab_service:
        is_available = await colab_service.test_connection()
        
        if is_available:
            print("✅ Colab connection successful!")
            return True
        else:
            print("❌ Colab connection failed!")
            return False

async def test_image_generation():
    """Test image generation with Colab"""
    print("\n🎨 Testing image generation...")
    
    test_cases = [
        {
            "prompt": "Breaking news about AI technology",
            "category": "technology"
        },
        {
            "prompt": "Political developments in Pakistan",
            "category": "conflict"
        },
        {
            "prompt": "Entertainment industry updates",
            "category": "entertainment"
        }
    ]
    
    async with ColabService() as colab_service:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {test_case['prompt']} ({test_case['category']})")
            
            try:
                result = await colab_service.generate_image(
                    prompt=test_case["prompt"],
                    category=test_case["category"]
                )
                
                if result["success"]:
                    print(f"   ✅ Generated image successfully")
                    print(f"   📝 Caption: {result['caption'][:50]}...")
                    print(f"   🎯 Source: {result['source']}")
                else:
                    print(f"   ❌ Generation failed")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

async def test_multiple_images():
    """Test multiple image generation"""
    print("\n🖼️ Testing multiple image generation...")
    
    async with ColabService() as colab_service:
        result = await colab_service.generate_multiple_images(
            prompt="Comprehensive news coverage",
            category="general",
            count=2
        )
        
        if result["success"]:
            print(f"✅ Generated {result['total_images']} images successfully")
            for i, img in enumerate(result["images"]):
                print(f"   Image {i+1}: {img['image_type']} - {img['style']}")
        else:
            print("❌ Multiple image generation failed")

async def main():
    """Main test function"""
    print("🚀 AuroraPress Module 4 - Colab Integration Test")
    print("=" * 60)
    
    # Test connection
    connection_ok = await test_colab_connection()
    
    if not connection_ok:
        print("\n❌ Cannot proceed - Colab connection failed")
        print("   Please check:")
        print("   1. Colab notebook is running")
        print("   2. ngrok URL is correct")
        print("   3. Internet connection is working")
        return
    
    # Test single image generation
    await test_image_generation()
    
    # Test multiple image generation
    await test_multiple_images()
    
    print("\n🎉 All tests completed!")
    print("   Your Colab integration is ready to use!")

if __name__ == "__main__":
    asyncio.run(main())








