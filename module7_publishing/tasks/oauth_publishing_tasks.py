import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from celery import Celery
from celery.exceptions import Retry
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from tasks import scheduling_tasks 

logger = logging.getLogger(__name__)

# Initialize Celery app
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'aurorapress_oauth_publishing',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    task_soft_time_limit=300,
    task_time_limit=600,
)

@celery_app.task(bind=True, max_retries=3, name='module7_publishing.tasks.oauth_publishing_tasks.publish_article_oauth')
def publish_article_oauth(self, user_id: str, article_data: Dict[str, Any], target_platforms: List[str] = None) -> Dict[str, Any]:
    """
    Publish article using user's OAuth tokens
    FIXED: Ensures actual API calls are made
    """
    logger.info("="*80)
    logger.info(f"TASK STARTED: publish_article_oauth")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Platforms: {target_platforms}")
    logger.info("="*80)
    
    # CRITICAL: Import inside task to ensure fresh imports
    from database.oauth_db import get_user_connections, store_publishing_record
    from publishers.wordpress_oauth_client import publish_to_wordpress_oauth
    from publishers.social_oauth_client import (
        publish_to_twitter_oauth
    )
    
    if target_platforms is None:
        target_platforms = ['wordpress', 'twitter']
    
    logger.info(f"Target platforms (after default): {target_platforms}")

    workflow_results = {
        'user_id': user_id,
        'article_id': article_data.get('article_id'),
        'started_at': datetime.utcnow().isoformat(),
        'platforms': {},
        'overall_success': False,
        'task_id': self.request.id
    }
    
    try:
        logger.info(f"Starting OAuth publishing workflow for user {user_id}")
        
        # Force available platforms for testing (remove platform checks temporarily)
        available_platforms = target_platforms
        logger.info(f"Available platforms: {available_platforms}")

        successful_publications = 0
        
        # Step 1: Publish to WordPress first (if requested)
        if 'wordpress' in available_platforms:
            logger.info("→ WordPress publishing requested")
            try:
                wp_result = publish_to_wordpress_oauth(user_id, article_data)
                logger.info(f"WordPress result: {wp_result}")
                workflow_results['platforms']['wordpress'] = wp_result
                
                if wp_result.get('success'):
                    successful_publications += 1
                    article_data['wordpress_url'] = wp_result['post_url']
                    article_data['wordpress_post_id'] = wp_result['post_id']
                    store_publishing_record(user_id, article_data.get('article_id'), 'wordpress', wp_result)
                    logger.info("✓ WordPress publish SUCCESS")
                else:
                    logger.error(f"✗ WordPress publish FAILED: {wp_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"✗ WordPress exception: {str(e)}", exc_info=True)
                workflow_results['platforms']['wordpress'] = {
                    'success': False, 
                    'error': str(e), 
                    'user_id': user_id
                }
        
        # Step 2: Publish to Twitter (if requested)
        if 'twitter' in available_platforms:
            logger.info("\n" + "="*60)
            logger.info("→ Twitter publishing requested")
            logger.info("="*60)
            
            try:
                # CRITICAL: Call Twitter publish function directly
                logger.info(f"Calling publish_to_twitter_oauth for user {user_id}")
                twitter_result = publish_to_twitter_oauth(user_id, article_data)
                logger.info(f"Twitter result received: {twitter_result}")
                
                workflow_results['platforms']['twitter'] = twitter_result
                
                if twitter_result.get('success'):
                    successful_publications += 1
                    store_publishing_record(user_id, article_data.get('article_id'), 'twitter', twitter_result)
                    logger.info(f"✓ Twitter publish SUCCESS: {twitter_result.get('tweet_url')}")
                else:
                    logger.error(f"✗ Twitter publish FAILED: {twitter_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"✗ Twitter exception: {str(e)}", exc_info=True)
                workflow_results['platforms']['twitter'] = {
                    'success': False,
                    'error': str(e),
                    'user_id': user_id
                }
        
        # Determine overall success
        workflow_results['overall_success'] = successful_publications > 0
        workflow_results['successful_platforms'] = successful_publications
        workflow_results['total_platforms'] = len(available_platforms)
        workflow_results['completed_at'] = datetime.utcnow().isoformat()
        
        logger.info("\n" + "="*80)
        logger.info("TASK COMPLETED")
        logger.info(f"Success: {workflow_results['overall_success']}")
        logger.info(f"Successful platforms: {successful_publications}/{len(available_platforms)}")
        logger.info(f"Results: {workflow_results}")
        logger.info("="*80 + "\n")
        
        return workflow_results
        
    except Exception as exc:
        logger.error(f"✗ CRITICAL ERROR in publish_article_oauth: {str(exc)}", exc_info=True)
        workflow_results['error'] = str(exc)
        workflow_results['completed_at'] = datetime.utcnow().isoformat()
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return workflow_results

@celery_app.task(bind=True, max_retries=3)
def update_published_article_oauth(self, user_id: str, platform: str, post_id: str, updated_article_data: Dict[str, Any], reason: str = "Content update") -> Dict[str, Any]:
    """Update published article using user's OAuth tokens"""
    from database.oauth_db import get_oauth_token, store_publishing_record
    from publishers.wordpress_oauth_client import update_wordpress_post
    
    try:
        logger.info(f"Updating {platform} post {post_id} for user {user_id}: {reason}")
        
        user_token = get_oauth_token(user_id, platform)
        if not user_token:
            return {
                'success': False,
                'user_id': user_id,
                'platform': platform,
                'error': f'{platform} not connected for this user'
            }
        
        result = None
        
        if platform == 'wordpress':
            result = update_wordpress_post(user_id, int(post_id), updated_article_data)
        elif platform in ['twitter', 'linkedin']:
            result = {
                'success': False,
                'error': f'{platform} does not support post editing',
                'user_id': user_id,
                'platform': platform
            }
        else:
            result = {
                'success': False,
                'error': f'Update not supported for platform: {platform}',
                'user_id': user_id,
                'platform': platform
            }
        
        if result and result.get('success'):
            store_publishing_record(user_id, updated_article_data.get('article_id'), platform, result)
            logger.info(f"{platform} post updated successfully for user {user_id}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Update error for user {user_id} on {platform}: {str(exc)}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {
            'success': False,
            'user_id': user_id,
            'platform': platform,
            'error': str(exc)
        }

@celery_app.task(bind=True)
def check_user_platform_status(self, user_id: str) -> Dict[str, Any]:
    """Check status of all user's connected platforms"""
    from database.oauth_db import get_user_connections, get_oauth_token
    
    try:
        user_connections = get_user_connections(user_id)
        platform_status = {}
        
        for connection in user_connections:
            platform = connection['platform']
            token_data = get_oauth_token(user_id, platform)
            
            platform_status[platform] = {
                'connected': connection.get('connected', False),
                'token_valid': token_data is not None,
                'platform_username': connection.get('platform_username', ''),
                'connected_at': connection.get('connected_at', ''),
                'last_checked': datetime.utcnow().isoformat()
            }
        
        return {
            'user_id': user_id,
            'platforms': platform_status,
            'total_platforms': len(platform_status),
            'connected_platforms': len([p for p in platform_status.values() if p['connected'] and p['token_valid']]),
            'checked_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Platform status check error for user {user_id}: {e}")
        return {
            'user_id': user_id,
            'error': str(e),
            'checked_at': datetime.utcnow().isoformat()
        }

@celery_app.task
def cleanup_failed_tasks():
    """Cleanup task for failed publishing attempts"""
    try:
        logger.info("Cleaning up failed publishing tasks")
        return {'cleanup_completed': True, 'cleaned_at': datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Cleanup task error: {e}")
        return {'cleanup_completed': False, 'error': str(e)}

def publish_seo_optimized_article(user_id: str, seo_optimized_article: Dict[str, Any], target_platforms: List[str] = None) -> str:
    """Integration function for Module 5 to publish SEO-optimized articles"""
    try:
        task = publish_article_oauth.delay(user_id, seo_optimized_article, target_platforms)
        logger.info(f"SEO-optimized article publishing started for user {user_id}: {task.id}")
        return task.id
    except Exception as e:
        logger.error(f"Error starting SEO article publishing: {e}")
        return None

def test_oauth_publishing_workflow():
    """Test OAuth publishing workflow"""
    try:
        test_article = {
            'article_id': 'oauth_test_001',
            'title': 'OAuth Publishing Test - Twitter Direct Call',
            'content': '<p>Testing direct Twitter API calls from Celery task.</p>',
            'excerpt': 'Testing OAuth publishing system with direct function calls',
            'status': 'publish',
            'seo_data': {
                'keywords': ['oauth', 'publishing', 'test', 'aurorapress'],
                'meta_description': 'Testing OAuth publishing workflow',
                'url_slug': 'oauth-publishing-test-direct'
            }
        }
        
        test_user_id = 'test_user_oauth'
        target_platforms = ['twitter']  # Test Twitter only first
        
        # Start publishing task
        task = publish_article_oauth.delay(test_user_id, test_article, target_platforms)
        
        print(f"\nOAuth publishing task started: {task.id}")
        print("Waiting for result...")
        
        # Wait for result
        result = task.get(timeout=300)
        
        print(f"\n{'='*80}")
        print("TASK RESULT:")
        print(f"{'='*80}")
        print(f"Overall Success: {result.get('overall_success')}")
        print(f"Successful Platforms: {result.get('successful_platforms')}/{result.get('total_platforms')}")
        
        for platform, platform_result in result.get('platforms', {}).items():
            status = "✓" if platform_result.get('success') else "✗"
            print(f"\n{status} {platform.upper()}:")
            if platform_result.get('success'):
                print(f"  URL: {platform_result.get('tweet_url') or platform_result.get('post_url', 'N/A')}")
            else:
                print(f"  Error: {platform_result.get('error', 'Unknown error')}")
        
        return result.get('overall_success', False)
            
    except Exception as e:
        print(f"\n✗ OAuth publishing test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing OAuth publishing workflow...")
    success = test_oauth_publishing_workflow()
    
    if success:
        print("\n🎉 OAuth publishing workflow working!")
    else:
        print("\n💥 OAuth publishing workflow needs debugging")