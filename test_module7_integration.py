#!/usr/bin/env python3
"""
Module 7 Integration Test Script
Tests the integration of Module 7 (Publishing) with AuroraPress
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_module7_availability():
    """Test if Module 7 is available and properly configured"""
    print("🔍 Testing Module 7 Availability")
    print("=" * 50)
    
    try:
        from module7_integration import is_module7_available, get_module7_info
        available = is_module7_available()
        info = get_module7_info()
        
        print(f"✅ Module 7 Available: {available}")
        print(f"✅ Status: {info.get('status', 'unknown')}")
        print(f"✅ Platforms: {info.get('platforms', [])}")
        
        if available:
            print("✅ Module 7 integration is working")
            return True
        else:
            print("❌ Module 7 integration is not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Module 7: {e}")
        return False

def test_backend_endpoints():
    """Test Module 7 backend endpoints"""
    print("\n🌐 Testing Backend Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test publishing info endpoint
    try:
        response = requests.get(f"{base_url}/api/publishing/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Publishing info endpoint: {data.get('status', 'unknown')}")
            print(f"   Available: {data.get('available', False)}")
            print(f"   Platforms: {data.get('platforms', [])}")
        else:
            print(f"❌ Publishing info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing publishing info: {e}")
    
    # Test user status endpoint
    try:
        response = requests.get(f"{base_url}/api/publishing/user/default_user/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User status endpoint: {len(data.get('connections', []))} connections")
        else:
            print(f"❌ User status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing user status: {e}")

def test_article_publishing():
    """Test article publishing functionality"""
    print("\n📝 Testing Article Publishing")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # First, get an article to test with
    try:
        response = requests.get(f"{base_url}/api/articles?limit=1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if articles and len(articles) > 0:
                article = articles[0]
                article_id = article.get('_id')
                print(f"✅ Found test article: {article_id}")
                print(f"   Title: {article.get('title', 'No title')[:50]}...")
                
                # Test publishing endpoint
                try:
                    publish_response = requests.post(
                        f"{base_url}/api/publishing/publish/{article_id}",
                        params={"user_id": "test_user", "target_platforms": ["twitter"]},
                        timeout=10
                    )
                    if publish_response.status_code == 200:
                        data = publish_response.json()
                        print(f"✅ Publishing started: {data.get('task_id', 'unknown')}")
                        print(f"   Status: {data.get('message', 'unknown')}")
                    else:
                        print(f"❌ Publishing failed: {publish_response.status_code}")
                        print(f"   Response: {publish_response.text}")
                except Exception as e:
                    print(f"❌ Error testing publishing: {e}")
            else:
                print("⚠️  No articles found to test publishing")
                print(f"   Response data: {data}")
        else:
            print(f"❌ Failed to get articles: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting articles: {e}")

def test_environment_variables():
    """Test Module 7 environment variables"""
    print("\n🔧 Testing Environment Variables")
    print("=" * 50)
    
    required_vars = [
        'REDIS_URL',
        'TWITTER_CLIENT_ID',
        'TWITTER_CLIENT_SECRET',
        'LINKEDIN_CLIENT_ID',
        'LINKEDIN_CLIENT_SECRET',
        'WORDPRESS_URL'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'SET' if value else 'NOT SET'}")
        else:
            print(f"⚠️  {var}: NOT SET (optional for testing)")

def main():
    """Run all Module 7 integration tests"""
    print("🚀 AuroraPress Module 7 Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Module 7 availability
    module7_available = test_module7_availability()
    
    # Test 2: Environment variables
    test_environment_variables()
    
    # Test 3: Backend endpoints (only if backend is running)
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            test_backend_endpoints()
            test_article_publishing()
        else:
            print("\n⚠️  Backend not running - skipping endpoint tests")
    except Exception:
        print("\n⚠️  Backend not running - skipping endpoint tests")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"   Module 7 Available: {'✅ YES' if module7_available else '❌ NO'}")
    print("   Next Steps:")
    
    if module7_available:
        print("   1. ✅ Module 7 is integrated successfully")
        print("   2. 🔧 Configure OAuth credentials in .env file")
        print("   3. 🚀 Start Redis server: redis-server")
        print("   4. 🎯 Test publishing with real OAuth credentials")
    else:
        print("   1. ❌ Module 7 integration failed")
        print("   2. 🔧 Check Module 7 dependencies are installed")
        print("   3. 🔧 Verify Module 7 files are in correct location")
        print("   4. 🔧 Check for import errors in module7_publishing")

if __name__ == "__main__":
    main()

