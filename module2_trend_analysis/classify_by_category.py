import os
from pymongo import MongoClient
from dotenv import load_dotenv
# Optional import for transformers
try:
    from transformers import pipeline
    HAVE_TRANSFORMERS = True
except ImportError:
    HAVE_TRANSFORMERS = False
    print("Warning: transformers not available. Category classification will be disabled.")

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["aurorapress"]
trends_col = db["dashboard_trends"]

# Define categories (make sure these match exactly with frontend)
CATEGORIES = [
    "politics",
    "technology",
    "science",
    "business",
    "entertainment",
    "sports",
    "conflict",
    "health"
]

def classify_trend(text, classifier):
    try:
        result = classifier(text, CATEGORIES)
        # Get top category and its score
        top_category = result["labels"][0].lower()
        score = result["scores"][0]
        return top_category, score
    except Exception as e:
        print(f"Error classifying text '{text}': {str(e)}")
        return "uncategorized", 0.0

def main():
    print("⚙️ Loading classification model...")
    if not HAVE_TRANSFORMERS:
        print("❌ Transformers not available. Skipping classification.")
        return
        
    try:
        classifier = pipeline("zero-shot-classification", 
                            model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load model: {str(e)}")
        return

    # Get all trends that don't have a category or have an empty category
    trends = list(trends_col.find())  # Get all trends for reclassification

    if not trends:
        print("No trends found in the database.")
        return

    print(f"🔍 Found {len(trends)} trends to classify...")
    updated = 0

    for i, trend in enumerate(trends):
        # Use both keyword and title for better classification
        text_to_classify = f"{trend.get('keyword', '')} {trend.get('title', '')}"
        category, confidence = classify_trend(text_to_classify, classifier)

        try:
            # Update the trend with the new category
            trends_col.update_one(
                {"_id": trend["_id"]},
                {"$set": {
                    "category": category,
                    "category_confidence": confidence
                }}
            )
            print(f"[{i+1}/{len(trends)}] ✅ '{trend.get('keyword', '')}' → {category} (confidence: {confidence:.2f})")
            updated += 1
        except Exception as e:
            print(f"❌ Error updating trend {trend.get('_id')}: {str(e)}")

    print(f"\n✅ Summary:")
    print(f"- Total trends processed: {len(trends)}")
    print(f"- Successfully categorized: {updated}")
    
    # Print category distribution
    print("\n📊 Category Distribution:")
    for category in CATEGORIES:
        count = trends_col.count_documents({"category": category})
        print(f"- {category}: {count} trends")

if __name__ == "__main__":
    main()
