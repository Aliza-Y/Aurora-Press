# debug_twitter_publishing.py
"""
Comprehensive debugging script for Twitter OAuth publishing
Run this to identify exactly where the publishing fails
"""

import sys
from pathlib import Path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_1_imports():
    """Test 1: Verify all imports work"""
    print("\n" + "="*80)
    print("TEST 1: Import Verification")
    print("="*80)
    
    try:
        from publishers.social_oauth_client import publish_to_twitter_oauth
        print("✓ publish_to_twitter_oauth imported successfully")
        
        from database.oauth_db import get_oauth_token
        print("✓ get_oauth_token imported successfully")
        
        import tweepy
        print(f"✓ tweepy imported successfully (version: {tweepy.__version__})")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_token_retrieval():
    """Test 2: Verify token retrieval from database"""
    print("\n" + "="*80)
    print("TEST 2: Token Retrieval")
    print("="*80)
    
    try:
        from database.oauth_db import get_oauth_token
        
        test_user_id = 'test_user_demo'
        token = get_oauth_token(test_user_id, 'twitter')
        
        if token:
            print(f"✓ Token retrieved for user {test_user_id}")
            print(f"  Token keys: {list(token.keys())}")
            print(f"  Has access_token: {'access_token' in token}")
            print(f"  Access token length: {len(token.get('access_token', ''))} chars")
            print(f"  Platform username: {token.get('platform_username', 'N/A')}")
            return True, token
        else:
            print(f"✗ No token found for user {test_user_id}")
            return False, None
            
    except Exception as e:
        print(f"✗ Token retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_3_twitter_client_creation(token_data):
    """Test 3: Verify Twitter client creation"""
    print("\n" + "="*80)
    print("TEST 3: Twitter Client Creation")
    print("="*80)
    
    try:
        from publishers.social_oauth_client import create_twitter_client
        
        access_token = token_data.get('access_token')
        print(f"Access token (first 20 chars): {access_token[:20]}...")
        
        client = create_twitter_client(access_token)
        
        if client:
            print("✓ Twitter client created successfully")
            
            # Test client by getting authenticated user
            try:
                me = client.get_me()
                if me.data:
                    print(f"✓ Client authenticated as: @{me.data.username}")
                    print(f"  User ID: {me.data.id}")
                    print(f"  Name: {me.data.name}")
                    return True, client
                else:
                    print("✗ Client created but get_me() returned no data")
                    return False, None
            except Exception as auth_error:
                print(f"✗ Client authentication failed: {auth_error}")
                return False, None
        else:
            print("✗ Failed to create Twitter client (returned None)")
            return False, None
            
    except Exception as e:
        print(f"✗ Client creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_4_content_preparation():
    """Test 4: Verify content preparation"""
    print("\n" + "="*80)
    print("TEST 4: Content Preparation")
    print("="*80)
    
    try:
        from publishers.social_oauth_client import prepare_twitter_content
        
        test_article = {
            'title': 'Test Article for Twitter Publishing Debug',
            'excerpt': 'This is a test article to debug Twitter publishing',
            'wordpress_url': 'https://test.com/article',
            'seo_data': {
                'keywords': ['test', 'debug', 'twitter']
            }
        }
        
        content = prepare_twitter_content(test_article)
        
        print("✓ Content prepared successfully")
        print(f"  Tweet text ({len(content['text'])} chars):")
        print(f"  {content['text']}")
        print(f"  Hashtags: {content.get('hashtags', [])}")
        
        if len(content['text']) > 280:
            print(f"⚠ Warning: Tweet exceeds 280 characters!")
            return False, content
        
        return True, content
        
    except Exception as e:
        print(f"✗ Content preparation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_5_tweet_posting(client, content):
    """Test 5: Actually post a tweet"""
    print("\n" + "="*80)
    print("TEST 5: Tweet Posting")
    print("="*80)
    
    try:
        from publishers.social_oauth_client import post_twitter_content
        
        print(f"Attempting to post tweet...")
        print(f"Tweet content: {content['text'][:100]}...")
        
        result = post_twitter_content(client, content)
        
        if result.get('success'):
            print("✓ Tweet posted successfully!")
            print(f"  Tweet ID: {result.get('tweet_id')}")
            print(f"  Tweet URL: {result.get('tweet_url')}")
            return True, result
        else:
            print(f"✗ Tweet posting failed: {result.get('error')}")
            return False, result
            
    except Exception as e:
        print(f"✗ Tweet posting exception: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_6_full_publishing_function():
    """Test 6: Test complete publish_to_twitter_oauth function"""
    print("\n" + "="*80)
    print("TEST 6: Full Publishing Function")
    print("="*80)
    
    try:
        from publishers.social_oauth_client import publish_to_twitter_oauth
        
        test_user_id = 'test_user_oauth'
        test_article = {
            'title': 'Full Function Test - Twitter OAuth Publishing',
            'content': 'Testing the complete Twitter OAuth publishing function',
            'excerpt': 'Full function test for Twitter publishing',
            'wordpress_url': 'https://test.com/full-test',
            'seo_data': {
                'keywords': ['oauth', 'test', 'full']
            }
        }
        
        print(f"Calling publish_to_twitter_oauth({test_user_id}, article_data)")
        result = publish_to_twitter_oauth(test_user_id, test_article)
        
        print(f"\nResult received:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"✓ Full publishing function worked!")
            print(f"  Tweet URL: {result.get('tweet_url')}")
            print(f"  Posted at: {result.get('posted_at')}")
            return True, result
        else:
            print(f"✗ Full publishing function failed:")
            print(f"  Error: {result.get('error')}")
            return False, result
            
    except Exception as e:
        print(f"✗ Full function exception: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_7_celery_task():
    """Test 7: Test Celery task execution"""
    print("\n" + "="*80)
    print("TEST 7: Celery Task Execution")
    print("="*80)
    
    try:
        from module7_publishing.tasks.oauth_publishing_tasks import publish_article_oauth
        
        test_user_id = 'test_user_oauth'
        test_article = {
            'article_id': 'celery_test_001',
            'title': 'Celery Task Test - Twitter Publishing',
            'content': '<p>Testing Celery task for Twitter publishing</p>',
            'excerpt': 'Celery task test',
            'wordpress_url': 'https://test.com/celery-test',
            'seo_data': {
                'keywords': ['celery', 'test', 'twitter']
            }
        }
        
        print("Starting Celery task...")
        task = publish_article_oauth.delay(test_user_id, test_article, ['twitter'])
        
        print(f"Task ID: {task.id}")
        print("Waiting for result (timeout: 60s)...")
        
        result = task.get(timeout=60)
        
        print(f"\nCelery task completed")
        print(f"  Overall success: {result.get('overall_success')}")
        print(f"  Successful platforms: {result.get('successful_platforms')}")
        
        if 'twitter' in result.get('platforms', {}):
            twitter_result = result['platforms']['twitter']
            if twitter_result.get('success'):
                print(f"✓ Celery task successfully posted to Twitter!")
                print(f"  Tweet URL: {twitter_result.get('tweet_url')}")
                return True, result
            else:
                print(f"✗ Celery task failed to post to Twitter:")
                print(f"  Error: {twitter_result.get('error')}")
                return False, result
        else:
            print("✗ Twitter platform not in results")
            return False, result
            
    except Exception as e:
        print(f"✗ Celery task exception: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def run_all_tests():
    """Run all debugging tests in sequence"""
    print("\n" + "="*80)
    print("TWITTER OAUTH PUBLISHING DEBUG SUITE")
    print("="*80)
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_1_imports()
    if not results['imports']:
        print("\n❌ Cannot proceed - imports failed")
        return results
    
    # Test 2: Token retrieval
    success, token_data = test_2_token_retrieval()
    results['token_retrieval'] = success
    if not success:
        print("\n❌ Cannot proceed - no token found")
        return results
    
    # Test 3: Client creation
    success, client = test_3_twitter_client_creation(token_data)
    results['client_creation'] = success
    if not success:
        print("\n❌ Cannot proceed - client creation failed")
        return results
    
    # Test 4: Content preparation
    success, content = test_4_content_preparation()
    results['content_preparation'] = success
    if not success:
        print("\n⚠ Content preparation failed, but continuing...")
    
    # Test 5: Tweet posting
    success, post_result = test_5_tweet_posting(client, content)
    results['tweet_posting'] = success
    if not success:
        print("\n⚠ Direct tweet posting failed")
    
    # Test 6: Full publishing function
    success, func_result = test_6_full_publishing_function()
    results['full_function'] = success
    if not success:
        print("\n⚠ Full publishing function failed")
    
    # Test 7: Celery task
    success, task_result = test_7_celery_task()
    results['celery_task'] = success
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, test_result in results.items():
        status = "✓ PASS" if test_result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Twitter publishing should be working.")
    else:
        print("\n❌ Some tests failed. Review the output above to identify issues.")
    
    return results


if __name__ == '__main__':
    import os
    
    print("Starting Twitter OAuth Publishing Debug Suite")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")
    
    results = run_all_tests()
    
    print("\n" + "="*80)
    print("Debug suite completed")
    print("="*80)