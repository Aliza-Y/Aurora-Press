#!/usr/bin/env python3
"""
🚀 AuroraPress Module 5 - SEO Integration Test Script
Tests the SEO optimization integration
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from module5_seo.services.seo_service import SEOService
from module5_seo.models.schemas import SEOOptimizationRequest

async def test_seo_optimization():
    """Test SEO optimization functionality"""
    print("🔍 Testing SEO optimization...")
    
    # Test article data
    test_article = {
        "title": "Breaking News: AI Technology Revolutionizes Journalism",
        "content": """
        Artificial Intelligence is transforming the journalism industry in unprecedented ways. 
        News organizations are adopting AI tools to enhance their reporting capabilities, 
        improve content quality, and reach wider audiences.
        
        The integration of AI in journalism has led to more efficient news production, 
        better fact-checking processes, and personalized content delivery. 
        Journalists can now focus on investigative work while AI handles routine tasks.
        
        However, this technological advancement also brings challenges. 
        Concerns about job displacement and the need for human oversight remain critical. 
        The industry must balance automation with journalistic integrity.
        """,
        "summary": "AI is revolutionizing journalism with enhanced reporting tools and automated processes.",
        "category": "technology"
    }
    
    try:
        # Create SEO service
        seo_service = SEOService()
        
        # Create request
        request = SEOOptimizationRequest(
            article_title=test_article["title"],
            article_content=test_article["content"],
            article_summary=test_article["summary"],
            category=test_article["category"]
        )
        
        print("   📝 Running SEO optimization...")
        result = await seo_service.optimize_article_simple(
            title=request.article_title,
            content=request.article_content
        )
        
        if result.get("success", True):
            print("   ✅ SEO optimization successful!")
            print(f"   📊 SEO Score: {result.get('seo_score', 0)}/100")
            print(f"   📖 Readability: {result.get('readability', {}).get('flesch', 0):.1f}")
            print(f"   🔑 Primary Keywords: {', '.join(result.get('keywords', {}).get('primary', [])[:3])}")
            print(f"   🎯 Intent: {result.get('intent', 'Unknown')}")
            print(f"   ⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
            
            # Show optimized title
            print(f"\n   📰 Original Title: {test_article['title']}")
            print(f"   📰 Optimized Title: {result.get('optimized_title', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ SEO optimization failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during SEO optimization: {e}")
        return False

async def test_seo_with_progress():
    """Test SEO optimization with progress tracking"""
    print("\n🔄 Testing SEO optimization with progress tracking...")
    
    test_article = {
        "title": "Climate Change Impact on Global Economy",
        "content": "Climate change is affecting global economic systems through various channels...",
        "summary": "Analysis of climate change economic impacts",
        "category": "business"
    }
    
    try:
        seo_service = SEOService()
        request = SEOOptimizationRequest(
            article_title=test_article["title"],
            article_content=test_article["content"],
            article_summary=test_article["summary"],
            category=test_article["category"]
        )
        
        # Add progress callback
        progress_updates = []
        
        def progress_callback(update):
            progress_updates.append(update)
            print(f"   📈 {update.step}: {update.message} ({update.progress}%)")
        
        seo_service.add_progress_callback("test_task", progress_callback)
        
        # Run optimization with progress
        result = await seo_service.optimize_article_with_progress(request, "test_task")
        
        if result.success:
            print("   ✅ Progress tracking test successful!")
            print(f"   📊 Final Score: {result.seo_score}/100")
            return True
        else:
            print(f"   ❌ Progress tracking test failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during progress tracking test: {e}")
        return False
    finally:
        seo_service.remove_progress_callback("test_task")

async def main():
    """Main test function"""
    print("🚀 AuroraPress Module 5 - SEO Integration Test")
    print("=" * 60)
    
    # Test basic SEO optimization
    basic_test = await test_seo_optimization()
    
    # Test progress tracking
    progress_test = await test_seo_with_progress()
    
    print("\n" + "=" * 60)
    if basic_test and progress_test:
        print("🎉 All SEO tests passed!")
        print("   Your SEO integration is ready to use!")
    else:
        print("❌ Some tests failed!")
        print("   Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
