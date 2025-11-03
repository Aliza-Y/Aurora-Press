#!/usr/bin/env python3
"""
Setup OAuth Connections for Module 7 Testing
Creates mock OAuth connections for testing publishing functionality
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_mock_oauth_connections():
    """Setup mock OAuth connections for testing"""
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
        
        # Create mock OAuth tokens for testing
        mock_tokens = [
            {
                "user_id": "default_user",
                "platform": "twitter",
                "access_token": "mock_twitter_token_12345",
                "refresh_token": "mock_twitter_refresh_12345",
                "token_type": "bearer",
                "scope": "tweet.read tweet.write users.read",
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "platform_user_id": "mock_twitter_user_123",
                "platform_username": "aurorapress_test",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": "default_user",
                "platform": "wordpress",
                "access_token": "mock_wordpress_token_67890",
                "refresh_token": "mock_wordpress_refresh_67890",
                "token_type": "bearer",
                "scope": "posts.read posts.write",
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "platform_user_id": "mock_wordpress_user_456",
                "platform_username": "aurorapress_test",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert or update OAuth tokens
        for token in mock_tokens:
            result = oauth_collection.replace_one(
                {"user_id": token["user_id"], "platform": token["platform"]},
                token,
                upsert=True
            )
            print(f"✅ {token['platform'].title()} OAuth token {'created' if result.upserted_id else 'updated'}")
        
        print(f"\n✅ Successfully setup OAuth connections for user: default_user")
        print("📋 Available platforms:")
        for token in mock_tokens:
            print(f"   - {token['platform'].title()}: @{token['platform_username']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up OAuth connections: {e}")
        return False

def main():
    """Main function to setup OAuth connections"""
    print("🔗 Setting up OAuth Connections for Module 7 Testing")
    print("=" * 60)
    
    success = setup_mock_oauth_connections()
    
    if success:
        print("\n✅ OAuth connections setup successfully!")
        print("🎯 You can now test publishing functionality")
        print("📋 Note: These are mock tokens for testing - real publishing requires actual OAuth credentials")
    else:
        print("\n❌ Failed to setup OAuth connections")
        print("🔧 Check your MongoDB connection and environment variables")

if __name__ == "__main__":
    main()



