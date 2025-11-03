"""
Module 7 Integration Helper for AuroraPress
Safe integration layer that doesn't modify existing code
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Module 7 availability flag
MODULE7_AVAILABLE = False

# Try to import Module 7 components
try:
    from module7_publishing.api.main_publishing_api import ArticleData, PublishRequest
    from module7_publishing.tasks.oauth_publishing_tasks import publish_article_oauth
    from module7_publishing.database.oauth_db import get_user_connections
    MODULE7_AVAILABLE = True
    logger.info("✅ Module 7 integration components loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️  Module 7 not available: {e}")
    MODULE7_AVAILABLE = False

def is_module7_available() -> bool:
    """Check if Module 7 is available and properly configured"""
    return MODULE7_AVAILABLE

def prepare_article_for_publishing(article: Dict[str, Any], user_id: str = "default_user") -> Optional[Dict[str, Any]]:
    """
    Prepare article data for Module 7 publishing
    Converts AuroraPress article format to Module 7 format
    """
    if not MODULE7_AVAILABLE:
        logger.warning("Module 7 not available - cannot prepare article for publishing")
        return None
    
    try:
        # Extract article data
        article_id = str(article.get('_id', ''))
        title = article.get('title', '')
        content = article.get('content', '')
        summary = article.get('summary', '')
        
        # Get SEO data if available
        seo_data = article.get('seo_optimization', {})
        
        # Get visual data if available
        visuals = article.get('visuals', [])
        featured_image_path = None
        if visuals:
            header_image = next((v for v in visuals if v.get('image_type') == 'header'), None)
            if header_image and header_image.get('image_data'):
                featured_image_path = header_image['image_data']
        
        # Prepare categories and tags
        categories = []
        tags = []
        
        # Add trend category
        trend_details = article.get('trend_details', {})
        if trend_details.get('category'):
            categories.append(trend_details['category'])
        
        if trend_details.get('keyword'):
            tags.append(trend_details['keyword'])
        
        # Add SEO keywords as tags
        if seo_data and seo_data.get('keywords'):
            seo_keywords = seo_data['keywords']
            if isinstance(seo_keywords, dict):
                primary_keywords = seo_keywords.get('primary', [])
                secondary_keywords = seo_keywords.get('secondary', [])
                tags.extend(primary_keywords)
                tags.extend(secondary_keywords)
        
        # Create ArticleData object
        article_data = {
            'article_id': article_id,
            'title': title,
            'content': content,
            'excerpt': summary,
            'featured_image_path': featured_image_path,
            'categories': categories,
            'tags': tags,
            'seo_data': seo_data,
            'status': 'publish'
        }
        
        logger.info(f"✅ Article prepared for publishing: {article_id}")
        return article_data
        
    except Exception as e:
        logger.error(f"❌ Error preparing article for publishing: {e}")
        return None

def publish_article_to_platforms(article: Dict[str, Any], user_id: str = "default_user", target_platforms: List[str] = None) -> Optional[Dict[str, Any]]:
    """
    Publish article to connected platforms using Module 7
    Returns publishing task information
    """
    if not MODULE7_AVAILABLE:
        logger.warning("Module 7 not available - cannot publish article")
        return None
    
    try:
        # Prepare article data
        article_data = prepare_article_for_publishing(article, user_id)
        if not article_data:
            return None
        
        # Start publishing task
        task = publish_article_oauth.delay(
            user_id,
            article_data,
            target_platforms
        )
        
        result = {
            'success': True,
            'message': 'Article publishing started',
            'task_id': task.id,
            'user_id': user_id,
            'article_id': article_data.get('article_id'),
            'target_platforms': target_platforms,
            'started_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Publishing task started: {task.id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error starting publishing task: {e}")
        return None

def get_user_publishing_status(user_id: str = "default_user") -> Optional[Dict[str, Any]]:
    """
    Get user's publishing platform connections and status
    """
    if not MODULE7_AVAILABLE:
        logger.warning("Module 7 not available - cannot get publishing status")
        return None
    
    try:
        connections = get_user_connections(user_id)
        return {
            'user_id': user_id,
            'connections': connections,
            'total_connections': len(connections),
            'retrieved_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting user publishing status: {e}")
        return None

def check_publishing_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Check the status of a publishing task
    """
    if not MODULE7_AVAILABLE:
        logger.warning("Module 7 not available - cannot check task status")
        return None
    
    try:
        from celery.result import AsyncResult
        from module7_publishing.tasks.oauth_publishing_tasks import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task is waiting to be processed'
            }
        elif result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task is being processed',
                'current': result.info.get('current', 0),
                'total': result.info.get('total', 1)
            }
        elif result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task completed successfully',
                'result': result.result
            }
        else:
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'Task failed',
                'error': str(result.info)
            }
            
        return response
        
    except Exception as e:
        logger.error(f"❌ Error checking task status: {e}")
        return None

# Convenience functions for easy integration
def can_publish_articles() -> bool:
    """Check if article publishing is available"""
    return MODULE7_AVAILABLE

def get_available_platforms() -> List[str]:
    """Get list of available publishing platforms"""
    if not MODULE7_AVAILABLE:
        return []
    
    return ['twitter', 'linkedin', 'wordpress']

def get_module7_info() -> Dict[str, Any]:
    """Get Module 7 information and status"""
    return {
        'available': MODULE7_AVAILABLE,
        'platforms': get_available_platforms(),
        'endpoints': {
            'publish_article': '/m7/publish/article',
            'oauth_twitter': '/m7/oauth/twitter/authorize',
            'oauth_linkedin': '/m7/oauth/linkedin/authorize',
            'user_connections': '/m7/user/{user_id}/connections',
            'task_status': '/m7/publish/status/{task_id}'
        } if MODULE7_AVAILABLE else {},
        'status': 'operational' if MODULE7_AVAILABLE else 'unavailable'
    }
