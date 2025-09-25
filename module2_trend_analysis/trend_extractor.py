import spacy
from pymongo import MongoClient
from collections import Counter
from dotenv import load_dotenv
from transformers import pipeline
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Load NLP models
nlp = spacy.load("en_core_web_sm")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define categories you want to support
CANDIDATE_CATEGORIES = ["Politics", "Technology", "Health", "Environment", "Conflict", "Economy", "Sports", "Culture"]

def extract_trends():
    # MongoDB setup
    client = MongoClient(MONGO_URI)
    db = client["aurorapress"]
    articles_col = db["rss_articles"]
    dashboard_col = db["dashboard_trends"]

    # Fetch latest 100 articles
    articles = articles_col.find().sort("published", -1).limit(100)
    entity_counter = Counter()

    print("🔍 Extracting named entities from articles...\n")

    # Extract entities
    for article in articles:
        text = article.get("title", "") + " " + article.get("summary", "")
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE"]:
                entity_counter[ent.text.strip()] += 1

    # Classify and store in dashboard_trends
    print("🧠 Classifying entities into categories...\n")
    for entity, count in entity_counter.items():
        try:
            result = classifier(entity, CANDIDATE_CATEGORIES)
            best_category = result["labels"][0]
        except Exception as e:
            best_category = "Uncategorized"

        dashboard_col.update_one(
            {"keyword": entity, "type": "NER"},
            {
                "$set": {
                    "score": count,
                    "type": "NER",
                    "source": "rss",
                    "category": best_category
                }
            },
            upsert=True
        )

    print("✅ NER-based trends with categories saved to dashboard_trends.\n")
    client.close()

if __name__ == "__main__":
    extract_trends()

