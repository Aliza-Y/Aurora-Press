from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Establish the database connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Create or reference the collection for storing RSS articles
rss_collection = db["rss_articles"]

# This code connects to your MongoDB database and makes a reference to a collection named rss_articles where your news articles will be saved.