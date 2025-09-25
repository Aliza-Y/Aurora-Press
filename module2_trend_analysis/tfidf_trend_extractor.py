import os
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
from dotenv import load_dotenv

print("🚀 Script started successfully")

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Load classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Device set to use", classifier.device)

# Define possible categories (you can tweak these)
candidate_labels = ["Politics", "Conflict", "Environment", "Technology", "Economy", "Health", "Science", "World", "Crime"]


def fetch_all_documents(articles_collection):
    docs = list(articles_collection.find({}, {"title": 1, "summary": 1, "_id": 0}))
    corpus = [doc["title"] + " " + doc.get("summary", "") for doc in docs]
    return corpus


def extract_top_keywords(corpus):
    if not corpus:
        return []
        
    # Initialize TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2),
        max_df=0.85,
        min_df=2
    )
    
    try:
        # Fit and transform the corpus
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate average TF-IDF scores for each term
        avg_scores = tfidf_matrix.mean(axis=0).A1
        
        # Create list of (term, score) tuples and sort by score
        keywords = [(term, score) for term, score in zip(feature_names, avg_scores)]
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        return keywords[:20]  # Return top 20 keywords
    except Exception as e:
        print(f"Error in TF-IDF extraction: {str(e)}")
        return []


def save_to_db(keywords, dashboard_col):
    for keyword, score in keywords:
        try:
            # Classify the keyword
            result = classifier(keyword, candidate_labels)
            category = result["labels"][0].lower()
            
            # Update the dashboard collection
            dashboard_col.update_one(
                {"keyword": keyword, "type": "TFIDF"},
                {
                    "$set": {
                        "score": float(score),
                        "category": category,
                        "source": "rss",
                        "type": "TFIDF"
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"Error processing keyword {keyword}: {str(e)}")


def extract_and_save_trends():
    print("🚀 Starting TF-IDF trend extraction")
    
    # MongoDB connection
    client = MongoClient(MONGO_URI)
    db = client["aurorapress"]
    articles_collection = db["rss_articles"]
    dashboard_col = db["dashboard_trends"]

    print("🔎 Fetching articles...")
    corpus = fetch_all_documents(articles_collection)

    print(f"📦 Corpus contents: {corpus[:1]}")  # Print just the first item for preview
    print(f"📊 Corpus size: {len(corpus)}")     # Show how many articles we fetched

    if not corpus:
        print("⚠️ No articles found in the database.")
    else:
        print(f"✅ Found {len(corpus)} articles. Extracting keywords...")

        top_keywords = extract_top_keywords(corpus)

        if not top_keywords:
            print("⚠️ No keywords extracted. Check your data or TF-IDF config.")
        else:
            print(f"✅ Extracted {len(top_keywords)} keywords. Saving to DB...")
            save_to_db(top_keywords, dashboard_col)
            print("✅ TF-IDF keyword trends saved successfully.")
    
    client.close()


if __name__ == "__main__":
    extract_and_save_trends()
