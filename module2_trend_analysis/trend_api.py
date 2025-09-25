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

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["aurorapress"]
dash_col = db["dashboard_trends"]

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
        output_json = process_article_request(json.dumps(article_input))
        output_data = json.loads(output_json)

        # Check if we have the required content
        if not output_data.get("article_text"):
            article_logger.error(f"No article_text in output data: {output_data}")
            raise HTTPException(status_code=500, detail="No content generated")

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
            }
        }

    except Exception as e:
        article_logger.exception(f"Error generating article: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles")
def get_articles(limit: int = 10, skip: int = 0):
    try:
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
