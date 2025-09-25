import os
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import sys
import os

# Add module3_article_generator to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'module3_article_generator'))
from articleGen import process_article_request
from datetime import datetime

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "aurorapress")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

approved_collection = db["approved_trends"]
generated_collection = db["generated_articles"]

# Fetch unprocessed approved trends
pending_trends = approved_collection.find({"article_generated": {"$ne": True}})

for trend in pending_trends:
    print(f"\n📝 Generating article for: {trend['title']}")

    # Prepare input for articleAgent
    input_data = {
        "title": trend["title"],
        "keywords": trend["keywords"],
        "summary": trend["summary"],
        "style": trend.get("style", "neutral"),
        "tone": trend.get("tone", "informative"),
        "length": trend.get("length", 500)
    }

    input_json = json.dumps(input_data)
    output_json = process_article_request(input_json)
    result = json.loads(output_json)

    if result["status"] == "success":
        print("✅ Article generated.")

        generated_collection.insert_one({
            "title": result["title"],
            "article_text": result["article_text"],
            "metadata": result["metadata"],
            "generated_timestamp": datetime.now().isoformat(),
            "source_trend_id": trend["_id"],
            "category": trend.get("category", "General")
        })

        # Mark trend as processed
        approved_collection.update_one(
            {"_id": trend["_id"]},
            {"$set": {"article_generated": True}}
        )
    else:
        print(f"❌ Failed to generate article: {result['message']}")
