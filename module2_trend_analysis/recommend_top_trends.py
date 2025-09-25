from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["aurorapress"]
collection = db["dashboard_trends"]

# Fetch top 10 trends sorted by score
top_trends = list(
    collection.find({}, {"_id": 0, "keyword": 1, "score": 1, "type": 1, "category": 1, "source": 1})
    .sort("score", -1)
    .limit(10)
)

# Print results
print("🔥 Top Trending Topics (Auto-Fetched):\n")
for i, trend in enumerate(top_trends, 1):
    print(f"{i}. {trend['keyword']} (score: {trend['score']}, type: {trend['type']}, category: {trend.get('category', 'N/A')})")
 