import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from module3_article_generator.agenticArticleGen import process_article_request
from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
import requests
import asyncio
from .classify_by_category import CATEGORIES

# Setup logging to logs/articles.log
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "articles.log")

article_logger = logging.getLogger("articles")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
article_logger.addHandler(handler)
article_logger.setLevel(logging.INFO)

# Load env variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB with proper Atlas configuration
try:
    # MongoDB Atlas connection with proper SSL/TLS settings
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=30000,  # 30 seconds
        connectTimeoutMS=30000,          # 30 seconds
        socketTimeoutMS=30000,           # 30 seconds
        retryWrites=True,
        retryReads=True,
        # Remove problematic SSL options for Atlas
        # tlsAllowInvalidCertificates and tlsAllowInvalidHostnames don't work with Atlas
    )
    # Test the connection
    client.admin.command('ping')
    db = client["aurorapress"]
    dash_col = db["dashboard_trends"]
    print("✅ MongoDB connection successful")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("🔄 Trying alternative connection method...")
    
    # Try alternative connection method
    try:
        # Alternative: Try with minimal SSL settings
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=True
        )
        client.admin.command('ping')
        db = client["aurorapress"]
        dash_col = db["dashboard_trends"]
        print("✅ MongoDB connection successful (alternative method)")
        FALLBACK_MODE = False
    except Exception as e2:
        print(f"❌ Alternative MongoDB connection also failed: {e2}")
        print("⚠️  Some features may not work without database connection")
        print("💡 Check your MongoDB Atlas network access settings")
        # Create a mock client for development
        client = None
        db = None
        dash_col = None
        
        # Add fallback data for development
        print("🔄 Using fallback data for development...")
        FALLBACK_MODE = True
else:
    FALLBACK_MODE = False

# FastAPI app
app = FastAPI()

# CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add default categories at the top
VALID_CATEGORIES = ["all"] + CATEGORIES

@app.get("/api/trends")
async def get_trends(category: Optional[str] = None, limit: int = 20):
    try:
        if dash_col is None:
            # Return fallback data for development
            fallback_trends = [
                {
                    "_id": "fallback_1",
                    "keyword": "Artificial Intelligence",
                    "score": 85,
                    "category": "technology",
                    "source": "system",
                    "status": "pending"
                },
                {
                    "_id": "fallback_2", 
                    "keyword": "Climate Change",
                    "score": 78,
                    "category": "environment",
                    "source": "system",
                    "status": "pending"
                },
                {
                    "_id": "fallback_3",
                    "keyword": "Space Exploration",
                    "score": 72,
                    "category": "science",
                    "source": "system", 
                    "status": "pending"
                }
            ]
            return {"trends": fallback_trends, "fallback": True}
        
        # Debug: Print all unique categories in the database
        all_categories = dash_col.distinct("category")
        print(f"Available categories in database: {all_categories}")

        query = {}
        if category and category.lower() != 'all':
            # Make the category search case-insensitive
            category_lower = category.lower()
            if category_lower in CATEGORIES:
                query["category"] = category_lower

        print(f"Fetching trends with query: {query}")  # Debug log
        results = list(dash_col.find(query).sort("score", -1).limit(limit))
        print(f"Found {len(results)} trends")  # Debug log
        
        trends = []
        for doc in results:
            # Ensure category is always set and lowercase
            if "category" not in doc or not doc["category"]:
                doc["category"] = "uncategorized"
            else:
                doc["category"] = doc["category"].lower()

            # Get associated RSS article for summary if available
            summary = doc.get("summary", "")
            if not summary and doc.get("source") == "rss":
                rss_article = db.rss_articles.find_one({"title": {"$regex": doc["keyword"], "$options": "i"}})
                if rss_article:
                    summary = rss_article.get("summary", "")

            trend = {
                "trend_id": str(doc["_id"]),
                "keyword": doc["keyword"],
                "title": generateDetailedTitle(doc),
                "score": doc["score"],
                "type": doc.get("type", "Unknown"),
                "category": doc["category"],
                "source": doc.get("source", "rss"),
                "source_url": doc.get("source_url", "https://www.bbc.com/news"),
                "summary": summary or "Click to view more details about this trending topic and its context.",
                "publication_date": doc.get("publication_date", datetime.utcnow().isoformat())
            }
            trends.append(trend)
            
        print(f"Processed {len(trends)} trends")  # Debug log
        return {"count": len(trends), "trends": trends}
    except Exception as e:
        print(f"Error in get_trends: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

def generateDetailedTitle(trend: dict) -> str:
    # Generate more meaningful titles based on the trend data
    titles = {
        'US': 'US Technology Innovation: Latest Developments in AI and Robotics',
        'Trump': 'Trump Legal Proceedings: Latest Updates and Implications',
        'Gaza': 'Gaza Crisis: Humanitarian Situation and Peace Negotiations',
        'China': 'China-Taiwan Relations: Economic and Diplomatic Developments',
        'India': "India's Economic Growth: New Policy Implementations",
        'Pakistan': 'Pakistan Political Landscape: Recent Electoral Developments',
        # Add more mappings as needed
    }
    
    # If we have a direct mapping, use it
    if trend["keyword"] in titles:
        return titles[trend["keyword"]]
    
    # Otherwise, generate a title based on the category
    category = trend.get("category", "General")
    return f"Latest Updates on {trend['keyword']} in {category}"

@app.post("/api/approve-topic")
def approve_topic(payload: dict = Body(...)):
    payload["timestamp"] = datetime.utcnow().isoformat()
    print(f"🟢 Article generation triggered for: {payload}")
    return {"status": "success", "message": "Topic approved and sent to article generation agent", "data": payload}


@app.get("/api/trends/{trend_id}")
async def get_trend_detail(trend_id: str):
    try:
        object_id = ObjectId(trend_id)
        trend = dash_col.find_one({"_id": object_id})
        
        if not trend:
            raise HTTPException(status_code=404, detail="Trend not found")

        # Get associated RSS article for more context
        summary = trend.get("summary", "")
        if not summary and trend.get("source") == "rss":
            rss_article = db.rss_articles.find_one({"title": {"$regex": trend["keyword"], "$options": "i"}})
            if rss_article:
                summary = rss_article.get("summary", "")
        
        response = {
            "trend_id": str(trend["_id"]),
            "keyword": trend["keyword"],
            "title": generateDetailedTitle(trend),
            "score": trend["score"],
            "type": trend.get("type", "Unknown"),
            "category": trend.get("category", "uncategorized").lower(),
            "source": trend.get("source", "rss"),
            "source_url": trend.get("source_url", "https://www.bbc.com/news"),
            "summary": summary or "No detailed summary available for this trend.",
            "publication_date": trend.get("publication_date", datetime.utcnow().isoformat())
        }
            
        return response
        
    except Exception as e:
        print(f"Error in get_trend_detail: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve_trend/{trend_id}")
async def approve_trend(trend_id: str):
    try:
        # Find the trend
        trend = db.dashboard_trends.find_one({"_id": ObjectId(trend_id)})
        if not trend:
            raise HTTPException(status_code=404, detail="Trend not found")

        # Convert ObjectId to string in trend document
        trend_id_str = str(trend["_id"])
        trend = {k: str(v) if isinstance(v, ObjectId) else v for k, v in trend.items()}

        # Get associated RSS article for more context
        rss_article = None
        if trend.get("source") == "rss":
            rss_article = db.rss_articles.find_one({"title": {"$regex": trend["keyword"], "$options": "i"}})
            if rss_article:
                rss_article = {k: str(v) if isinstance(v, ObjectId) else v for k, v in rss_article.items()}

        # Prepare article input
        trend_context = f"Breaking news about {trend['keyword']} in the {trend.get('category', 'general')} sector. "
        if rss_article and rss_article.get('summary'):
            trend_context += rss_article['summary']
        if trend.get('description'):
            trend_context += f" {trend['description']}"
        if trend.get('source'):
            trend_context += f" This development was reported by {trend['source']}."

        # Prepare keywords
        keywords = [trend["keyword"]]
        if trend.get("category"):
            keywords.append(trend["category"])
        if trend.get("type"):
            keywords.append(trend["type"])
        if trend.get("additional_keywords"):
            keywords.extend(trend["additional_keywords"])

        article_input = {
            "title": generateDetailedTitle(trend),
            "keywords": keywords,
            "summary": trend_context,
            "style": trend.get("style", "neutral"),
            "tone": trend.get("tone", "informative"),
            "length": trend.get("length", 500)
        }

        # Call the article generation script
        try:
            output_json = process_article_request(json.dumps(article_input))
            output_data = json.loads(output_json)

            # Check if we have the required content
            if not output_data.get("article_text"):
                article_logger.error(f"No article_text in output data: {output_data}")
                raise HTTPException(status_code=500, detail="No content generated")
        except Exception as e:
            article_logger.error(f"Error generating article: {e}")
            # Create a fallback article when API fails
            fallback_content = f"""
{article_input['title']}

{trend_context}

This is a breaking news article about {trend['keyword']} in the {trend.get('category', 'general')} sector. 

The development was reported by {trend.get('source', 'multiple sources')} and represents a significant development in the field.

Key points:
• This story involves {trend['keyword']}
• It falls under the {trend.get('category', 'general')} category
• The source is {trend.get('source', 'verified news outlets')}
• This represents ongoing developments in the sector

Further details will be updated as more information becomes available.

---
Note: This article was generated using fallback content due to API limitations. For full AI-generated content, please ensure your API keys are properly configured.
"""
            output_data = {
                "article_text": fallback_content,
                "headline": article_input['title'],
                "summary": trend_context,
                "metadata": {
                    "generated_timestamp": datetime.utcnow().isoformat(),
                    "fallback_mode": True
                }
            }

        # Create the article document
        article_doc = {
            "title": output_data.get("headline", output_data.get("title", article_input["title"])),
            "content": output_data["article_text"],
            "summary": output_data.get("summary", trend_context),
            "metadata": {
                "word_count": output_data.get("metadata", {}).get("article", {}).get("word_count", 
                    len(output_data["article_text"].split())),
                "generated_timestamp": output_data.get("metadata", {}).get("generated_timestamp", 
                    datetime.utcnow().isoformat())
            },
            "trend_details": {
                "keyword": trend["keyword"],
                "category": trend.get("category", "Uncategorized"),
                "source": trend.get("source", "System")
            }
        }

        # Store the generated article
        insert_result = db.generated_articles.insert_one(article_doc)
        inserted_id_str = str(insert_result.inserted_id)
        
        # Update the trend status
        db.dashboard_trends.update_one(
            {"_id": ObjectId(trend_id)},
            {"$set": {
                "article_generated": True,
                "status": "generated",
                "generated_article_id": inserted_id_str,
                "last_updated": datetime.utcnow().isoformat()
            }}
        )
        
        article_logger.info(f"Successfully generated and stored article for trend: {trend['keyword']}")
        print(f"DEBUG: About to start visual generation for trend: {trend['keyword']}")
        
        # Generate visuals for the article using Colab GPU
        print("DEBUG: VISUAL GENERATION CODE IS BEING EXECUTED!")
        try:
            article_logger.info("Starting visual generation...")
            print(f"DEBUG: Starting visual generation for article: {article_doc['title']}")
            
            # Import Colab service
            from Module4_visual_generation.services.colab_service import ColabService
            from Module4_visual_generation.colab_config import colab_config
            
            # Test Colab connection first
            async with ColabService() as colab_service:
                is_colab_available = await colab_service.test_connection()
                
                if is_colab_available:
                    print(f"DEBUG: Colab GPU available! Generating real AI images...")
                    article_logger.info("Using Colab GPU for visual generation")
                    
                    # Generate images using Colab
                    visual_result = await colab_service.generate_multiple_images(
                        prompt=article_doc['title'],
                        category=trend.get("category", "general"),
                        count=2
                    )
                    
                    if visual_result["success"]:
                        print(f"DEBUG: Colab generation successful! Generated {visual_result['total_images']} images")
                        article_logger.info(f"Generated {visual_result['total_images']} images using Colab GPU")
                        
                        # Convert to our format
                        images = visual_result["images"]
                        print(f"DEBUG: Converted {len(images)} images to our format")
                    else:
                        print(f"DEBUG: Colab generation failed, falling back to enhanced mock")
                        visual_result = None
                else:
                    print(f"DEBUG: Colab not available, falling back to enhanced mock")
                    visual_result = None
                
                # Fallback to enhanced mock if Colab fails
                if not visual_result or not visual_result.get("success"):
                    print(f"DEBUG: Using enhanced mock visual generation")
                    article_logger.info("Using enhanced mock visual generation")
                    
                    # Generate enhanced mock images
                    images = []
                    
                    # Generate header image
                    header_caption = f"Header image for: {article_doc['title']}"
                    header_image = create_enhanced_mock_image(trend.get("category", "general"), "header", article_doc['title'])
                    
                    images.append({
                        "image_id": f"header_{trend.get('category', 'general')}_{len(images)}",
                        "image_data": header_image,
                        "caption": header_caption,
                        "image_type": "header",
                        "style": "realistic" if trend.get("category", "general") in ["politics", "business", "technology", "science", "conflict"] else "artistic"
                    })
                    
                    # Generate inline image
                    inline_caption = f"Related to: {', '.join(keywords[:3])}"
                    inline_image = create_enhanced_mock_image(trend.get("category", "general"), "inline", article_doc['title'])
                    
                    images.append({
                        "image_id": f"inline_{trend.get('category', 'general')}_{len(images)}",
                        "image_data": inline_image,
                        "caption": inline_caption,
                        "image_type": "inline",
                        "style": "realistic" if trend.get("category", "general") in ["politics", "business", "technology", "science", "conflict"] else "artistic"
                    })
                    
                    print(f"DEBUG: Generated {len(images)} enhanced mock images")
            
            print(f"DEBUG: Generated {len(images)} images, updating database...")
            print(f"DEBUG: Images data: {images[0] if images else 'No images'}")
            
            # Update article document with visual data
            update_result = db.generated_articles.update_one(
                {"_id": insert_result.inserted_id},
                {"$set": {
                    "visuals": images,
                    "visual_generation_metadata": {
                        "generated": True,
                        "total_images": len(images),
                        "generation_time": 0.5,  # Mock generation time
                        "source": "colab_gpu" if any(img.get("source") == "colab_gpu" for img in images) else "mock_fallback"
                    }
                }}
            )
            print(f"DEBUG: Database update result: {update_result.modified_count} documents modified")
            print(f"DEBUG: Article ID: {insert_result.inserted_id}")
            article_logger.info(f"Successfully generated {len(images)} visuals")
                
        except Exception as visual_error:
            print(f"DEBUG: Visual generation error: {str(visual_error)}")
            article_logger.warning(f"Visual generation failed: {str(visual_error)}, continuing without visuals")
        
        # SEO Optimization Step
        print(f"DEBUG: Starting SEO optimization for article: {article_doc['title']}")
        try:
            article_logger.info("Starting SEO optimization...")
            
            # Import SEO service
            from module5_seo.services.seo_service import SEOService
            from module5_seo.models.schemas import SEOOptimizationRequest
            
            # Create SEO optimization request
            seo_request = SEOOptimizationRequest(
                article_title=article_doc['title'],
                article_content=article_doc['content'],
                article_summary=article_doc['summary'],
                category=trend.get("category", "general")
            )
            
            # Run SEO optimization
            seo_service = SEOService()
            seo_result = await seo_service.optimize_article_simple(
                title=seo_request.article_title,
                content=seo_request.article_content
            )
            
            if seo_result.get("success", True):
                print(f"DEBUG: SEO optimization successful! Score: {seo_result.get('seo_score', 0)}")
                article_logger.info(f"SEO optimization completed with score: {seo_result.get('seo_score', 0)}")
                
                # Update article with SEO optimized content
                seo_update_result = db.generated_articles.update_one(
                    {"_id": insert_result.inserted_id},
                    {"$set": {
                        "seo_optimization": {
                            "optimized_title": seo_result.get("optimized_title", article_doc['title']),
                            "meta_description": seo_result.get("meta_description", ""),
                            "optimized_content": seo_result.get("optimized_content", article_doc['content']),
                            "keywords": seo_result.get("keywords", {}),
                            "intent": seo_result.get("intent", "informational"),
                            "readability": seo_result.get("readability", {}),
                            "structure": seo_result.get("structure", {}),
                            "seo_score": seo_result.get("seo_score", 0),
                            "slug": seo_result.get("slug", ""),
                            "optimized_at": seo_result.get("optimized_at", ""),
                            "processing_time": seo_result.get("processing_time", 0)
                        },
                        "seo_optimized": True
                    }}
                )
                
                print(f"DEBUG: SEO database update result: {seo_update_result.modified_count} documents modified")
                article_logger.info("Successfully applied SEO optimization to article")
            else:
                print(f"DEBUG: SEO optimization failed: {seo_result.get('error', 'Unknown error')}")
                article_logger.warning(f"SEO optimization failed: {seo_result.get('error', 'Unknown error')}")
                
        except Exception as seo_error:
            print(f"DEBUG: SEO optimization error: {str(seo_error)}")
            article_logger.warning(f"SEO optimization failed: {str(seo_error)}, continuing without SEO optimization")
        
        # Return a consistent response structure
        return {
            "status": "success",
            "message": "Article generated successfully",
            "_id": inserted_id_str,  # This is the main article ID for redirection
            "article": {
                "_id": inserted_id_str,
                "title": article_doc["title"],
                "summary": article_doc["summary"],
                "trend_details": article_doc["trend_details"]
            },
            "debug": "Visual generation code was reached"
        }

    except Exception as e:
        article_logger.exception(f"Error generating article: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles")
def get_articles(limit: int = 10, skip: int = 0):
    try:
        if db is None:
            # Return fallback data for development
            fallback_articles = [
                {
                    "_id": "fallback_article_1",
                    "title": "Sample Article: AI in Journalism",
                    "content": "This is a sample article about artificial intelligence in journalism...",
                    "summary": "Exploring the impact of AI on modern journalism practices.",
                    "metadata": {
                        "word_count": 500,
                        "generated_timestamp": "2024-01-15T10:00:00Z"
                    },
                    "trend_details": {
                        "keyword": "Artificial Intelligence",
                        "category": "technology",
                        "source": "system"
                    }
                }
            ]
            return {"count": 1, "total": 1, "articles": fallback_articles, "hasMore": False, "fallback": True}
        
        # Get total count of articles
        total_count = db.generated_articles.count_documents({})
        
        # Sort by generated_timestamp in descending order (newest first)
        results = db.generated_articles.find().sort([
            ("metadata.generated_timestamp", -1)
        ]).skip(skip).limit(limit)
        
        articles = []
        
        for doc in results:
            try:
                # Convert ObjectId to string
                doc_id = str(doc["_id"])
                
                # Create a properly structured article document
                article = {
                    "_id": doc_id,
                    "title": doc.get("title", "Untitled"),
                    "content": doc.get("content", ""),
                    "summary": doc.get("summary", "No summary available"),
                    "metadata": {
                        "word_count": doc.get("metadata", {}).get("word_count", 0),
                        "generated_timestamp": doc.get("metadata", {}).get("generated_timestamp", 
                            datetime.utcnow().isoformat())
                    },
                    "trend_details": {
                        "keyword": doc.get("trend_details", {}).get("keyword", "Unknown"),
                        "category": doc.get("trend_details", {}).get("category", "Uncategorized"),
                        "source": doc.get("trend_details", {}).get("source", "System")
                    }
                }
                
                # Add visuals if present
                if "visuals" in doc:
                    article["visuals"] = doc["visuals"]
                
                # Add visual generation metadata if present
                if "visual_generation_metadata" in doc:
                    article["visual_generation_metadata"] = doc["visual_generation_metadata"]
                
                # Add SEO optimization data if present
                if "seo_optimization" in doc:
                    article["seo_optimization"] = doc["seo_optimization"]
                
                # Add SEO optimization flag
                if "seo_optimized" in doc:
                    article["seo_optimized"] = doc["seo_optimized"]
                
                articles.append(article)
                
            except Exception as doc_error:
                print(f"Error processing document {doc.get('_id')}: {str(doc_error)}")
                continue
        
        print(f"Retrieved {len(articles)} articles")  # Debug log
        return {
            "count": len(articles),
            "total": total_count,
            "articles": articles,
            "hasMore": skip + limit < total_count
        }
        
    except Exception as e:
        print(f"Error in get_articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommended-topics")
def recommend_top_topics(limit: int = 10):
    try:
        # Sort by score in descending order and get top trends
        results = dash_col.find({}, {
            "_id": 1,
            "keyword": 1,
            "score": 1,
            "type": 1,
            "category": 1,
            "source": 1,
            "source_url": 1,
            "summary": 1
        }).sort("score", -1).limit(limit)
        
        recommended = []
        for doc in results:
            # Convert ObjectId to string
            doc["_id"] = str(doc["_id"])
            # Ensure category is lowercase
            if "category" in doc:
                doc["category"] = doc["category"].lower()
            recommended.append(doc)
        
        return {"count": len(recommended), "recommended": recommended}
    except Exception as e:
        print(f"Error in recommend_top_topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/articles/{article_id}")
def get_article(article_id: str):
    try:
        # Validate article_id
        if not article_id or article_id == "undefined" or len(article_id) != 24:
            raise HTTPException(status_code=400, detail="Invalid article ID")
            
        article = db.generated_articles.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Format the article data with proper structure and serialization
        formatted_article = {
            "_id": str(article["_id"]),
            "title": article.get("title", "Untitled"),
            "content": article.get("content", ""),
            "summary": article.get("summary", "No summary available"),
            "metadata": {
                "word_count": article.get("metadata", {}).get("word_count", 0),
                "generated_timestamp": article.get("metadata", {}).get("generated_timestamp", 
                    article.get("last_updated", datetime.utcnow().isoformat()))
            }
        }

        # Add visuals if present
        if "visuals" in article:
            formatted_article["visuals"] = article["visuals"]
        
        # Add visual generation metadata if present
        if "visual_generation_metadata" in article:
            formatted_article["visual_generation_metadata"] = article["visual_generation_metadata"]
        
        # Add SEO optimization data if present
        if "seo_optimization" in article:
            formatted_article["seo_optimization"] = article["seo_optimization"]
        
        # Add SEO optimization flag
        if "seo_optimized" in article:
            formatted_article["seo_optimized"] = article["seo_optimized"]

        # Handle trend details if present
        if "trend_details" in article:
            trend_details = article["trend_details"]
            if isinstance(trend_details, dict):
                # Convert any ObjectId in trend_details to string
                if "_id" in trend_details:
                    trend_details["_id"] = str(trend_details["_id"])
                formatted_article["trend_details"] = {
                    "keyword": trend_details.get("keyword", "Unknown"),
                    "category": trend_details.get("category", "Uncategorized"),
                    "source": trend_details.get("source", "System")
                }
            else:
                formatted_article["trend_details"] = {
                    "keyword": "Unknown",
                    "category": "Uncategorized",
                    "source": "System"
                }

        return formatted_article
    except Exception as e:
        print(f"Error fetching article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a new endpoint to get available categories
@app.get("/api/categories")
async def get_categories():
    try:
        # Return predefined categories
        return {"categories": CATEGORIES}
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def delete_article(article_id: str):
    try:
        result = db.generated_articles.delete_one({"_id": ObjectId(article_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        return {"status": "success", "message": "Article deleted successfully"}
    except Exception as e:
        print(f"Error deleting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_article_visuals(article_title: str, article_content: str, article_summary: str, category: str, keywords: list):
    """Generate visuals for an article using Module 4."""
    try:
        # Generate mock visuals directly
        article_logger.info("Starting mock visual generation...")
        
        # Create mock images based on category
        images = []
        
        # Generate header image
        header_caption = f"Header image for: {article_title}"
        header_image = create_mock_svg_image(category, "header")
        
        images.append({
            "image_id": f"header_{category}_{len(images)}",
            "image_data": header_image,
            "caption": header_caption,
            "image_type": "header",
            "style": "realistic" if category in ["politics", "business", "technology", "science"] else "artistic"
        })
        
        # Generate inline image
        inline_caption = f"Related to: {', '.join(keywords[:3])}"
        inline_image = create_mock_svg_image(category, "inline")
        
        images.append({
            "image_id": f"inline_{category}_{len(images)}",
            "image_data": inline_image,
            "caption": inline_caption,
            "image_type": "inline",
            "style": "realistic" if category in ["politics", "business", "technology", "science"] else "artistic"
        })
        
        visual_data = {
            "success": True,
            "images": images,
            "message": f"Generated {len(images)} mock images for {category} article",
            "total_images": len(images),
            "generation_time": 0.5
        }
        
        article_logger.info(f"Visual generation successful: {visual_data['message']}")
        return visual_data
            
    except Exception as e:
        article_logger.error(f"Error in visual generation: {str(e)}")
        return None

def create_enhanced_mock_image(category: str, image_type: str, article_title: str = "") -> str:
    """Create a more realistic-looking mock image as base64."""
    import base64
    import random
    
    # Define realistic color schemes and visual elements based on category
    category_themes = {
        'politics': {
            'bg': '#1e293b', 'accent': '#3b82f6', 'text': '#ffffff',
            'elements': ['🏛️', '📊', '🗳️', '⚖️'], 'style': 'professional'
        },
        'business': {
            'bg': '#0f172a', 'accent': '#10b981', 'text': '#ffffff',
            'elements': ['📈', '💼', '💰', '📊'], 'style': 'corporate'
        },
        'technology': {
            'bg': '#1e1b4b', 'accent': '#8b5cf6', 'text': '#ffffff',
            'elements': ['💻', '🤖', '🔬', '⚡'], 'style': 'futuristic'
        },
        'science': {
            'bg': '#7c2d12', 'accent': '#f97316', 'text': '#ffffff',
            'elements': ['🧪', '🔬', '🌍', '⚗️'], 'style': 'scientific'
        },
        'conflict': {
            'bg': '#7f1d1d', 'accent': '#ef4444', 'text': '#ffffff',
            'elements': ['⚔️', '🛡️', '🌍', '⚖️'], 'style': 'serious'
        },
        'entertainment': {
            'bg': '#581c87', 'accent': '#ec4899', 'text': '#ffffff',
            'elements': ['🎭', '🎬', '🎵', '🎨'], 'style': 'artistic'
        },
        'health': {
            'bg': '#14532d', 'accent': '#22c55e', 'text': '#ffffff',
            'elements': ['🏥', '💊', '❤️', '⚕️'], 'style': 'medical'
        },
        'sports': {
            'bg': '#1e40af', 'accent': '#3b82f6', 'text': '#ffffff',
            'elements': ['⚽', '🏆', '🏃', '💪'], 'style': 'dynamic'
        }
    }
    
    theme = category_themes.get(category.lower(), category_themes['politics'])
    
    # Create a more realistic SVG with better visual elements
    svg_content = f"""
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{theme['bg']};stop-opacity:1" />
                <stop offset="50%" style="stop-color:{theme['accent']};stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:{theme['bg']};stop-opacity:0.8" />
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge> 
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background -->
        <rect width="400" height="300" fill="url(#bg)"/>
        
        <!-- Decorative elements -->
        <circle cx="80" cy="80" r="25" fill="{theme['accent']}" opacity="0.2"/>
        <circle cx="320" cy="100" r="35" fill="{theme['accent']}" opacity="0.15"/>
        <circle cx="350" cy="250" r="20" fill="{theme['accent']}" opacity="0.25"/>
        <circle cx="50" cy="220" r="30" fill="{theme['accent']}" opacity="0.2"/>
        
        <!-- Main content area -->
        <rect x="50" y="100" width="300" height="120" fill="rgba(255,255,255,0.05)" rx="10"/>
        
        <!-- Category icon/emoji -->
        <text x="200" y="140" text-anchor="middle" fill="{theme['accent']}" font-family="Arial, sans-serif" font-size="32" filter="url(#glow)">
            {random.choice(theme['elements'])}
        </text>
        
        <!-- Category name -->
        <text x="200" y="170" text-anchor="middle" fill="{theme['text']}" font-family="Arial, sans-serif" font-size="18" font-weight="bold">
            {category.upper()}
        </text>
        
        <!-- Image type -->
        <text x="200" y="190" text-anchor="middle" fill="{theme['text']}" font-family="Arial, sans-serif" font-size="12" opacity="0.8">
            {image_type.title()} • {theme['style'].title()}
        </text>
        
        <!-- AuroraPress branding -->
        <text x="200" y="250" text-anchor="middle" fill="{theme['text']}" font-family="Arial, sans-serif" font-size="10" opacity="0.6">
            AuroraPress AI • Generated Image
        </text>
    </svg>
    """
    
    # Convert SVG to base64
    svg_bytes = svg_content.encode('utf-8')
    base64_image = base64.b64encode(svg_bytes).decode('utf-8')
    
    return f"data:image/svg+xml;base64,{base64_image}"

def create_mock_svg_image(category: str, image_type: str) -> str:
    """Legacy function - redirects to enhanced mock image."""
    return create_enhanced_mock_image(category, image_type)

async def generate_article_visuals_http(article_title: str, article_content: str, article_summary: str, category: str, keywords: list):
    """Fallback HTTP-based visual generation."""
    try:
        # Prepare request data for Module 4
        visual_request = {
            "article_title": article_title,
            "article_content": article_content,
            "article_summary": article_summary,
            "category": category,
            "keywords": keywords,
            "max_images": 2
        }
        
        # Call Module 4 visual generation service via HTTP
        response = requests.post(
            "http://localhost:8000/m4/generate-simple",
            json=visual_request,
            timeout=30  # Reduced timeout to 30 seconds
        )
        
        if response.status_code == 200:
            visual_data = response.json()
            article_logger.info(f"Visual generation successful: {visual_data.get('message', 'Generated images')}")
            return visual_data
        else:
            article_logger.warning(f"Visual generation service returned status {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        article_logger.warning(f"Visual generation service not available: {str(e)}")
        return None
    except Exception as e:
        article_logger.error(f"Error in HTTP visual generation: {str(e)}")
        return None
