#!/usr/bin/env python3
"""
Setup Real OAuth Connections for Module 7
Uses actual credentials from .env file to create real OAuth connections
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_real_oauth_connections():
    """Setup real OAuth connections using credentials from .env"""
    try:
        from pymongo import MongoClient
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
        oauth_collection = db["oauth_tokens"]
        
        # Get real credentials from .env
        twitter_client_id = os.getenv("TWITTER_CLIENT_ID")
        twitter_client_secret = os.getenv("TWITTER_CLIENT_SECRET")
        twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        wordpress_url = os.getenv("WORDPRESS_URL")
        wordpress_username = os.getenv("WORDPRESS_USERNAME")
        wordpress_app_password = os.getenv("WORDPRESS_APP_PASSWORD")
        
        # Check if we have the required credentials
        if not all([twitter_client_id, twitter_client_secret, twitter_access_token, twitter_access_secret]):
            print("❌ Missing Twitter credentials in .env file")
            return False
            
        if not all([wordpress_url, wordpress_username, wordpress_app_password]):
            print("❌ Missing WordPress credentials in .env file")
            return False
        
        # Create real OAuth tokens
        real_tokens = [
            {
                "user_id": "default_user",
                "platform": "twitter",
                "access_token": twitter_access_token,
                "refresh_token": twitter_access_secret,  # Using access secret as refresh
                "token_type": "bearer",
                "scope": "tweet.read tweet.write users.read",
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "platform_user_id": "real_twitter_user",
                "platform_username": "aurorapress_real",
                "client_id": twitter_client_id,
                "client_secret": twitter_client_secret,
                "bearer_token": twitter_bearer_token,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": "default_user",
                "platform": "wordpress",
                "access_token": wordpress_app_password,  # WordPress uses app password as token
                "refresh_token": wordpress_app_password,
                "token_type": "basic",
                "scope": "posts.read posts.write",
                "expires_at": datetime.utcnow() + timedelta(days=365),  # WordPress app passwords don't expire
                "platform_user_id": wordpress_username,
                "platform_username": wordpress_username,
                "site_url": wordpress_url,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert or update OAuth tokens
        for token in real_tokens:
            result = oauth_collection.replace_one(
                {"user_id": token["user_id"], "platform": token["platform"]},
                token,
                upsert=True
            )
            print(f"✅ {token['platform'].title()} OAuth token {'created' if result.upserted_id else 'updated'} with REAL credentials")
        
        print(f"\n✅ Successfully setup REAL OAuth connections for user: default_user")
        print("📋 Available platforms with REAL credentials:")
        for token in real_tokens:
            print(f"   - {token['platform'].title()}: @{token['platform_username']}")
            if token['platform'] == 'twitter':
                print(f"     Client ID: {token['client_id'][:10]}...")
            elif token['platform'] == 'wordpress':
                print(f"     Site URL: {token['site_url']}")
        
        print("\n🎯 REAL PUBLISHING IS NOW ENABLED!")
        print("⚠️  WARNING: This will make REAL posts to your social media accounts!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up real OAuth connections: {e}")
        return False

def main():
    """Main function to setup real OAuth connections"""
    print("🔗 Setting up REAL OAuth Connections for Module 7")
    print("=" * 60)
    print("⚠️  WARNING: This will enable REAL publishing to your social media accounts!")
    print("=" * 60)
    
    # Auto-proceed for now (can be changed back to interactive later)
    print("✅ Proceeding with REAL publishing setup...")
    # response = input("Do you want to proceed with REAL publishing? (yes/no): ").lower().strip()
    # if response not in ['yes', 'y']:
    #     print("❌ Setup cancelled. Mock publishing will continue.")
    #     return
    
    success = setup_real_oauth_connections()
    
    if success:
        print("\n✅ REAL OAuth connections setup successfully!")
        print("🎯 You can now make REAL posts to Twitter and WordPress")
        print("📋 Remember to restart Celery worker to pick up the new tokens")
    else:
        print("\n❌ Failed to setup real OAuth connections")
        print("🔧 Check your .env file and MongoDB connection")

if __name__ == "__main__":
    main()
