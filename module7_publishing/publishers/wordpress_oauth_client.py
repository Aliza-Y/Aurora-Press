import mimetypes
import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

import requests
import base64
import time
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from database.oauth_db import get_oauth_token

logger = logging.getLogger(__name__)

def publish_to_wordpress_oauth(user_id: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
    """MOCK: Publish article to WordPress for demo purposes"""
    try:
        logger.info("="*60)
        logger.info(f"WordPress Publishing (MOCK) for user: {user_id}")
        logger.info("="*60)
        
        # Mock authentication check
        logger.info("✓ Mock WordPress authentication successful")
        
        # Prepare post data
        post_data = prepare_wordpress_post(article_data)
        
        # Mock successful posting
        post_id = f"mock_post_{int(time.time())}"
        post_url = f"https://aurorapressdemo.wuaze.com/mock-post/{post_id}"
        
        logger.info(f"✓ Mock WordPress post created successfully!")
        logger.info(f"  Post ID: {post_id}")
        logger.info(f"  Post URL: {post_url}")
        logger.info(f"  Title: {post_data['title']}")
        
        return {
            'success': True,
            'post_id': post_id,
            'post_url': post_url,
            'platform': 'wordpress',
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'mock': True
        }
        
    except Exception as e:
        logger.error(f"Mock WordPress publishing error: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'user_id': user_id,
            'platform': 'wordpress'
        }

def upload_wordpress_media(site_url: str, credentials: str, image_path: str) -> Optional[int]:
    """Upload media and return ID"""
    try:
        image_file = Path(image_path)
        
        if not image_file.exists():
            logger.error(f"Image not found: {image_path}")
            return None
        
        file_size = image_file.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(image_file))
        if not mime_type:
            mime_type = 'image/jpeg'
        
        logger.info(f"Uploading {image_file.name} ({file_size} bytes)")
        
        encoded_creds = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_creds}',
            'Content-Disposition': f'attachment; filename="{image_file.name}"',
            'Content-Type': mime_type
        }
        
        with open(image_file, 'rb') as f:
            image_data = f.read()
        
        response = requests.post(
            f"{site_url}/wp-json/wp/v2/media",
            headers=headers,
            data=image_data,
            timeout=60
        )
        
        logger.info(f"Media upload response: {response.status_code}")
        
        if response.status_code == 201:
            media_id = response.json()['id']
            logger.info(f"✓ Media ID: {media_id}")
            return media_id
        else:
            logger.error(f"Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        return None

def publish_wordpress_post(site_url: str, credentials: str, post_data: Dict[str, Any], featured_media_id: Optional[int] = None) -> Dict[str, Any]:
    """Create WordPress post with featured image"""
    try:
        encoded_creds = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_creds}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'title': post_data['title'],
            'content': post_data['content'],
            'excerpt': post_data.get('excerpt', ''),
            'status': post_data.get('status', 'publish'),
            'comment_status': 'open',
            'ping_status': 'open',
            'format': 'standard'
        }
        
        # CRITICAL: Add featured_media
        if featured_media_id:
            payload['featured_media'] = featured_media_id
            logger.info(f"→ Attaching media ID: {featured_media_id}")
        
        # Tags removed - WordPress API expects tag IDs, not names
        
        logger.info(f"Creating post: {payload['title']}")
        logger.info(f"Featured media: {featured_media_id or 'None'}")
        
        response = requests.post(
            f"{site_url}/wp-json/wp/v2/posts",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"Post creation response: {response.status_code}")
        
        if response.status_code == 201:
            post_resp = response.json()
            logger.info(f"✓ Post created: ID {post_resp['id']}")
            logger.info(f"  Featured media in response: {post_resp.get('featured_media', 'None')}")
            
            return {
                'success': True,
                'post_id': post_resp['id'],
                'post_url': post_resp['link'],
                'status': payload['status'],
                'featured_media_id': featured_media_id,
                'published_at': datetime.utcnow().isoformat()
            }
        else:
            error_msg = response.json().get('message', response.text) if response.text else str(response.status_code)
            return {'success': False, 'error': f"API error {response.status_code}: {error_msg}"}
            
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}
    
def prepare_wordpress_post(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare post data"""
    seo_data = article_data.get('seo_data', {})
    keywords = seo_data.get('keywords', [])
    
    return {
        'title': article_data.get('title', 'Untitled'),
        'content': article_data.get('content', '<p>No content</p>'),
        'excerpt': article_data.get('excerpt', ''),
        'status': article_data.get('status', 'publish')
        # Removed 'tags' - WordPress API expects tag IDs, not names
    }

def upload_featured_image(site_url: str, credentials: str, post_id: int, image_path: str) -> Dict[str, Any]:
    """
    Upload featured image to WordPress post
    
    Args:
        site_url: WordPress site URL
        credentials: "username:password" format
        post_id: WordPress post ID
        image_path: Path to image file
        
    Returns:
        Upload result
    """
    try:
        # Check if image exists
        from pathlib import Path
        image_file = Path(image_path)
        
        if not image_file.exists():
            return {'success': False, 'error': f'Image not found: {image_path}'}
        
        # Prepare upload
        media_url = f"{site_url}/wp-json/wp/v2/media"
        
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Disposition': f'attachment; filename="{image_file.name}"'
        }
        
        # Read image file
        with open(image_file, 'rb') as f:
            image_data = f.read()
        
        # Upload image
        response = requests.post(
            media_url,
            headers=headers,
            data=image_data,
            timeout=30
        )
        
        if response.status_code == 201:
            media_response = response.json()
            media_id = media_response['id']
            
            # Set as featured image
            post_url = f"{site_url}/wp-json/wp/v2/posts/{post_id}"
            update_response = requests.post(
                post_url,
                headers={'Authorization': f'Basic {encoded_credentials}'},
                json={'featured_media': media_id},
                timeout=10
            )
            
            if update_response.status_code == 200:
                return {
                    'success': True,
                    'media_id': media_id,
                    'message': 'Featured image set'
                }
        
        return {'success': False, 'error': 'Image upload failed'}
        
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        return {'success': False, 'error': str(e)}

def update_wordpress_post(user_id: str, post_id: int, updated_article_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update existing post"""
    try:
        wp_token = get_oauth_token(user_id, 'wordpress')
        if not wp_token:
            return {'success': False, 'error': 'Not connected'}
        
        site_url = wp_token.get('site_url', '').rstrip('/')
        credentials = wp_token.get('access_token', '')
        
        encoded_creds = base64.b64encode(credentials.encode()).decode()
        headers = {'Authorization': f'Basic {encoded_creds}', 'Content-Type': 'application/json'}
        
        post_data = prepare_wordpress_post(updated_article_data)
        payload = {
            'title': post_data['title'],
            'content': post_data['content'],
            'excerpt': post_data.get('excerpt', ''),
            'status': post_data.get('status', 'publish')
        }
        
        # Tags removed - WordPress API expects tag IDs, not names
        
        response = requests.post(f"{site_url}/wp-json/wp/v2/posts/{post_id}", headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return {'success': True, 'post_id': post_id, 'post_url': response.json()['link'], 'updated_at': datetime.utcnow().isoformat()}
        else:
            return {'success': False, 'error': f"Update failed: {response.status_code}"}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Test function
def test_wordpress_publishing():
    """Test WordPress publishing"""
    try:
        test_article = {
            'article_id': 'wp_test_001',
            'title': 'Test Article - WordPress REST API',
            'content': '<p>This is a test article published via WordPress REST API.</p><p>Testing complete Module 7 integration.</p>',
            'excerpt': 'Testing WordPress REST API publishing',
            'status': 'draft',  # Use draft for testing
            'seo_data': {
                'keywords': ['wordpress', 'rest', 'api', 'test'],
                'meta_description': 'Testing WordPress publishing'
            }
        }
        
        test_user_id = 'test_user_demo'
        
        result = publish_to_wordpress_oauth(test_user_id, test_article)
        
        if result['success']:
            print(f"✓ WordPress publishing successful!")
            print(f"  Post URL: {result['post_url']}")
            return True
        else:
            print(f"✗ WordPress publishing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wordpress_connection(site_url: str, username: str, password: str) -> Dict[str, Any]:
    """Test connection"""
    try:
        site_url = site_url.rstrip('/')
        credentials = f"{username}:{password}"
        encoded_creds = base64.b64encode(credentials.encode()).decode()
        headers = {'Authorization': f'Basic {encoded_creds}'}
        
        response = requests.get(f"{site_url}/wp-json/wp/v2/users/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            return {'success': True, 'user_id': user_data.get('id'), 'username': user_data.get('username'), 'site_url': site_url}
        else:
            return {'success': False, 'error': f'Failed: {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    print("Testing WordPress Publishing...")
    success = test_wordpress_publishing()
    
    if success:
        print("\nWordPress publishing working!")
    else:
        print("\nWordPress publishing needs configuration")