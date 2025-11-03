#!/usr/bin/env python3
"""
Create Test Articles for Module 7 Testing
Generates sample articles for testing publishing functionality
"""

import os
import sys
import json
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_articles():
    """Create test articles for Module 7 testing"""
    
    # Sample articles with different categories and content
    test_articles = [
        {
            "title": "AI Revolution in Journalism: How Machine Learning is Transforming News",
            "content": """
The journalism industry is experiencing a seismic shift as artificial intelligence and machine learning technologies reshape how news is created, distributed, and consumed. From automated content generation to personalized news feeds, AI is revolutionizing every aspect of modern journalism.

## The Rise of Automated Journalism

News organizations are increasingly turning to AI-powered tools to generate routine news stories, particularly in areas like financial reporting, sports updates, and weather forecasts. These systems can process vast amounts of data and produce coherent, fact-based articles in seconds.

## Personalization and Audience Engagement

Machine learning algorithms are enabling news platforms to deliver highly personalized content to individual readers. By analyzing reading patterns, social media activity, and demographic data, AI systems can curate news feeds that match each user's interests and preferences.

## Fact-Checking and Verification

AI tools are becoming indispensable for journalists in verifying information and detecting misinformation. Advanced natural language processing can quickly cross-reference claims against multiple sources and flag potentially false information.

## The Future of Journalism

As AI technology continues to advance, journalists will need to adapt and learn to work alongside these powerful tools. The future of journalism lies not in replacing human reporters, but in augmenting their capabilities with intelligent automation.

The transformation is already underway, and news organizations that embrace these technologies will be better positioned to serve their audiences in the digital age.
            """,
            "summary": "Exploring how AI and machine learning are transforming the journalism industry, from automated content generation to personalized news delivery.",
            "category": "technology",
            "keywords": ["AI", "journalism", "machine learning", "automation", "news technology"]
        },
        {
            "title": "Climate Change Impact on Global Food Security",
            "content": """
Climate change poses one of the most significant threats to global food security in the 21st century. Rising temperatures, changing precipitation patterns, and extreme weather events are already affecting agricultural production worldwide.

## Agricultural Challenges

Farmers around the world are facing unprecedented challenges as traditional growing seasons shift and weather patterns become more unpredictable. Crops that once thrived in certain regions are now struggling to adapt to new climate conditions.

## Water Scarcity and Irrigation

Water scarcity is becoming a critical issue for agriculture, particularly in regions already prone to drought. The changing climate is affecting water availability, forcing farmers to adopt more efficient irrigation methods and drought-resistant crop varieties.

## Economic Implications

The economic impact of climate change on agriculture extends far beyond individual farms. Food prices are becoming more volatile, and supply chains are increasingly vulnerable to climate-related disruptions.

## Adaptation Strategies

Governments, researchers, and farmers are working together to develop adaptation strategies. These include developing climate-resistant crop varieties, implementing sustainable farming practices, and investing in agricultural technology.

The challenge is immense, but with coordinated global action, we can work towards a more resilient and sustainable food system that can withstand the impacts of climate change.
            """,
            "summary": "Examining how climate change is affecting global food production and the strategies being developed to ensure food security.",
            "category": "science",
            "keywords": ["climate change", "food security", "agriculture", "sustainability", "environment"]
        },
        {
            "title": "The Future of Remote Work: Trends and Predictions for 2024",
            "content": """
The remote work revolution that began during the pandemic has fundamentally changed how we think about work, productivity, and workplace culture. As we move into 2024, several key trends are shaping the future of remote work.

## Hybrid Work Models

Most organizations are adopting hybrid work models that combine remote and in-office work. This approach offers flexibility while maintaining some level of face-to-face collaboration and company culture.

## Technology Infrastructure

The success of remote work depends heavily on robust technology infrastructure. Companies are investing heavily in cloud-based collaboration tools, secure communication platforms, and project management software.

## Mental Health and Work-Life Balance

Remote work has brought both benefits and challenges to employee mental health. While it offers flexibility and eliminates commuting stress, it can also lead to isolation and difficulty separating work from personal life.

## Productivity and Performance

Studies show that remote workers can be just as productive as their office-based counterparts, but this requires proper management, clear communication, and the right tools and processes.

## The Future Outlook

As technology continues to evolve and companies refine their remote work policies, we can expect to see even more innovative approaches to distributed work. The future of work is likely to be more flexible, technology-driven, and focused on results rather than location.

Remote work is not just a temporary response to the pandemic—it's a fundamental shift in how we approach work and life balance.
            """,
            "summary": "Analyzing current trends in remote work and predicting how the workplace will continue to evolve in 2024 and beyond.",
            "category": "business",
            "keywords": ["remote work", "hybrid work", "productivity", "workplace culture", "technology"]
        }
    ]
    
    return test_articles

def save_articles_to_database():
    """Save test articles to the database"""
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            print("❌ MONGO_URI not found in environment variables")
            return False
        
        client = MongoClient(mongo_uri)
        db = client["aurorapress"]
        articles_collection = db["generated_articles"]
        
        # Get test articles
        test_articles = create_test_articles()
        
        # Prepare articles for database
        articles_to_insert = []
        for i, article in enumerate(test_articles):
            article_doc = {
                "_id": ObjectId(),
                "title": article["title"],
                "content": article["content"],
                "summary": article["summary"],
                "metadata": {
                    "word_count": len(article["content"].split()),
                    "generated_timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat()
                },
                "trend_details": {
                    "keyword": article["keywords"][0],
                    "category": article["category"],
                    "source": "test_data"
                },
                "visuals": [
                    {
                        "image_id": f"test_image_{i+1}",
                        "image_type": "header",
                        "image_data": f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMWUyOTNiIi8+CiAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIyNCIgZmlsbD0iIzJkZDRiZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkF1cm9yYVByZXNzIFRlc3QgSW1hZ2Uge2krMX08L3RleHQ+Cjwvc3ZnPg==",
                        "caption": f"Test image for {article['title'][:50]}...",
                        "style": "realistic"
                    }
                ],
                "visual_generation_metadata": {
                    "generated": True,
                    "total_images": 1,
                    "generation_time": 2.5
                },
                "seo_optimized": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            articles_to_insert.append(article_doc)
        
        # Insert articles
        result = articles_collection.insert_many(articles_to_insert)
        
        print(f"✅ Successfully created {len(result.inserted_ids)} test articles")
        print("📝 Test articles created:")
        for i, article in enumerate(test_articles):
            print(f"   {i+1}. {article['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test articles: {e}")
        return False

def main():
    """Main function to create test articles"""
    print("🚀 Creating Test Articles for Module 7")
    print("=" * 50)
    
    success = save_articles_to_database()
    
    if success:
        print("\n✅ Test articles created successfully!")
        print("🎯 You can now test Module 7 publishing functionality")
        print("📋 Run: python test_module7_integration.py")
    else:
        print("\n❌ Failed to create test articles")
        print("🔧 Check your MongoDB connection and environment variables")

if __name__ == "__main__":
    main()
