import feedparser
from db import rss_collection
from datetime import datetime

# Define your RSS sources
RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "CNN Top Stories": "http://rss.cnn.com/rss/edition.rss"
}


def fetch_rss():
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        print(f"\n🔎 Fetching from {source}...")

        for entry in feed.entries:
            article = {
                "source": source,
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link,
                "published": entry.get("published", str(datetime.utcnow()))
            }

            # Avoid duplicates by checking if article with same link exists
            if not rss_collection.find_one({"link": article["link"]}):
                rss_collection.insert_one(article)
                print(f"✅ Inserted: {article['title']}")
            else:
                print(f"⏭️ Skipped (already exists): {article['title']}")


if __name__ == "__main__":
    fetch_rss()