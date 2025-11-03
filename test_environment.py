#!/usr/bin/env python3
"""
Environment Test Script for AuroraPress
Tests all required environment variables and connections
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test all environment variables and connections"""
    print("🔍 Testing AuroraPress Environment Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test MongoDB
    print("\n📊 Testing MongoDB Connection...")
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("❌ MONGO_URI not set")
        print("   Please set MONGO_URI in your .env file")
    else:
        print(f"✅ MONGO_URI is set: {mongo_uri[:20]}...")
        try:
            from pymongo import MongoClient
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("✅ MongoDB connection successful")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
    
    # Test Groq API
    print("\n🤖 Testing Groq API Configuration...")
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("❌ GROQ_API_KEY not set")
        print("   Please set GROQ_API_KEY in your .env file")
        print("   Get your key from: https://console.groq.com/")
    else:
        print(f"✅ GROQ_API_KEY is set: {groq_key[:10]}...")
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            # Test with a simple request
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Groq API connection successful")
            else:
                print(f"❌ Groq API error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Groq API test failed: {e}")
    
    # Test other optional variables
    print("\n🔧 Testing Optional Configuration...")
    
    colab_url = os.getenv("COLAB_API_URL")
    if colab_url:
        print(f"✅ COLAB_API_URL is set: {colab_url}")
    else:
        print("ℹ️  COLAB_API_URL not set (optional for Module 4)")
    
    groq_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    print(f"✅ GROQ_MODEL: {groq_model}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Create a .env file with your API keys")
    print("2. Copy the template from ENVIRONMENT_SETUP.md")
    print("3. Fill in your actual API keys")
    print("4. Restart the backend server")
    print("5. Test article generation")

if __name__ == "__main__":
    test_environment()




