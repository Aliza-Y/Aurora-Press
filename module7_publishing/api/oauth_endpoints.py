import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import HTTPBearer
import requests
import secrets
import hashlib
import base64
from urllib.parse import urlencode, parse_qs
import logging
from typing import Dict, Any, Optional
import base64, hashlib, secrets
from datetime import datetime, timedelta

from config.settings import settings
import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from database.oauth_db import store_oauth_token, get_oauth_token, get_user_connections, disconnect_platform

logger = logging.getLogger(__name__)
security = HTTPBearer()

# OAuth state storage (in production, use Redis)
oauth_states = {}

# Twitter OAuth 2.0 with PKCE functions
def generate_pkce_challenge():
    """Generate PKCE code verifier and challenge"""
    # Generate random code verifier
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generate code challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge

def generate_oauth_state(user_id: str, platform: str) -> str:
    """Generate and store OAuth state for CSRF protection"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        'user_id': user_id,
        'platform': platform,
        'created_at': datetime.utcnow()
    }
    return state

def validate_oauth_state(state: str) -> Optional[Dict[str, Any]]:
    """Validate OAuth state and return stored data"""
    if state in oauth_states:
        state_data = oauth_states.pop(state)  # Remove after use
        return state_data
    return None

def initiate_twitter_oauth(user_id: str) -> str:
    """Twitter OAuth 2.0 with PKCE and write permissions"""
    try:
        # Generate PKCE challenge
        code_verifier, code_challenge = generate_pkce_challenge()
        
        # Generate state for CSRF protection
        state = generate_oauth_state(user_id, 'twitter')
        
        # Store code verifier with state
        if state in oauth_states:
            oauth_states[state]['code_verifier'] = code_verifier
        
        # Build authorization URL with write scope
        auth_params = {
            'response_type': 'code',
            'client_id': settings.TWITTER_CLIENT_ID,
            'redirect_uri': f"http://localhost:{settings.API_PORT}/auth/twitter/callback",
            'scope': 'tweet.read tweet.write users.read offline.access',  # Ensure tweet.write is included
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(auth_params)}"
        return auth_url
        
    except Exception as e:
        logger.error(f"Error initiating Twitter OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def debug_oauth_states():
    """Debug function to check OAuth states"""
    return {
        "total_states": len(oauth_states),
        "states": {k: {
            "user_id": v.get('user_id'),
            "platform": v.get('platform'), 
            "has_code_verifier": 'code_verifier' in v,
            "created_at": v.get('created_at').isoformat() if v.get('created_at') else None
        } for k, v in oauth_states.items()}
    }

def handle_twitter_oauth_callback(code: str, state: str) -> Dict[str, Any]:
    """
    Handle Twitter OAuth callback and exchange code for tokens
    """
    logger.debug(f"OAuth states available: {list(oauth_states.keys())}")  ### Remove
    logger.debug(f"Incoming state: {state}") ### Remove
    try:
        # Validate state
        state_data = validate_oauth_state(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid OAuth state")
        
        user_id = state_data['user_id']
        code_verifier = state_data['code_verifier']

        token_url = "https://api.twitter.com/2/oauth2/token"

        # Build Basic Auth header instead of putting client_id/secret in body
        basic_auth = base64.b64encode(
            f"{settings.TWITTER_CLIENT_ID}:{settings.TWITTER_CLIENT_SECRET}".encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:8002/auth/twitter/callback",
            "code_verifier": code_verifier
        }

        response = requests.post(token_url, data=token_data, headers=headers)

        if response.status_code != 200:
            logger.error(f"Twitter token exchange failed: {response.status_code} - {response.text}")
            raise HTTPException(status_code=400, detail="Token exchange failed")

        token_response = response.json()

        # Get user information
        user_info = get_twitter_user_info(token_response['access_token'])

        token_storage_data = {
            "access_token": token_response['access_token'],
            "refresh_token": token_response.get('refresh_token'),
            "expires_in": token_response.get('expires_in', 7200),
            "token_type": token_response.get('token_type', 'bearer'),
            "scope": token_response.get('scope', ''),
            "platform_user_id": user_info.get('id', ''),
            "platform_username": user_info.get('username', '')
        }

        store_result = store_oauth_token(user_id, 'twitter', token_storage_data)

        if store_result:
            logger.info(f"Twitter OAuth completed for user: {user_id} (@{user_info.get('username')})")
            return {
                "success": True,
                "user_id": user_id,
                "platform": "twitter",
                "platform_user_id": user_info.get('id'),
                "platform_username": user_info.get('username'),
                "connected_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store OAuth token")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling Twitter OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

def get_twitter_user_info(access_token: str) -> Dict[str, Any]:
    """Get Twitter user information using access token"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.twitter.com/2/users/me?user.fields=id,username,name,profile_image_url',
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json().get('data', {})
            return user_data
        else:
            logger.error(f"Failed to get Twitter user info: {response.status_code}")
            return {}
            
    except Exception as e:
        logger.error(f"Error getting Twitter user info: {e}")
        return {}

# WordPress connection (simplified - can be credential or OAuth)
def connect_wordpress_site(user_id: str, site_url: str, username: str, password: str) -> Dict[str, Any]:
    """
    Connect WordPress site using credentials
    
    Args:
        user_id: User identifier
        site_url: WordPress site URL
        username: WordPress username
        password: WordPress password or app password
        
    Returns:
        Connection result
    """
    try:
        # Test WordPress connection
        test_result = test_wordpress_connection(site_url, username, password)
        
        if test_result['success']:
            # Store WordPress credentials as "token" for consistency
            wp_token_data = {
                'access_token': f"{username}:{password}",  # Encode credentials
                'site_url': site_url,
                'username': username,
                'expires_in': 31536000,  # 1 year (credentials don't expire)
                'token_type': 'credentials',
                'platform_user_id': test_result.get('user_id', ''),
                'platform_username': username
            }
            
            store_result = store_oauth_token(user_id, 'wordpress', wp_token_data)
            
            if store_result:
                logger.info(f"WordPress site connected for user: {user_id} - {site_url}")
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'platform': 'wordpress',
                    'site_url': site_url,
                    'platform_username': username,
                    'connected_at': datetime.utcnow().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to store WordPress credentials'}
        else:
            return {'success': False, 'error': test_result.get('error', 'WordPress connection failed')}
            
    except Exception as e:
        logger.error(f"Error connecting WordPress site: {e}")
        return {'success': False, 'error': str(e)}

def test_wordpress_connection(site_url: str, username: str, password: str) -> Dict[str, Any]:
    """Test WordPress connection"""
    try:
        import base64
        
        # Clean up URL
        site_url = site_url.rstrip('/')
        api_url = f"{site_url}/wp-json/wp/v2"
        
        # Create auth header
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        # Test connection by getting user info
        response = requests.get(f"{api_url}/users/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                'success': True,
                'user_id': user_data.get('id', ''),
                'username': user_data.get('username', ''),
                'name': user_data.get('name', '')
            }
        else:
            return {
                'success': False,
                'error': f'WordPress API error: {response.status_code}'
            }
            
    except Exception as e:
        return {'success': False, 'error': f'Connection test failed: {str(e)}'}

# Utility functions for token validation
def validate_user_token(user_id: str, platform: str) -> bool:
    """Check if user has valid token for platform"""
    token_data = get_oauth_token(user_id, platform)
    return token_data is not None

def get_user_platform_info(user_id: str, platform: str) -> Optional[Dict[str, Any]]:
    """Get platform-specific user information"""
    token_data = get_oauth_token(user_id, platform)
    
    if token_data:
        return {
            'platform': platform,
            'platform_user_id': token_data.get('platform_user_id', ''),
            'platform_username': token_data.get('platform_username', ''),
            'connected': True,
            'expires_at': token_data.get('expires_at', ''),
            'scope': token_data.get('scope', '')
        }
    else:
        return None

# OAuth cleanup functions
def cleanup_oauth_states():
    """Clean up expired OAuth states (call periodically)"""
    current_time = datetime.utcnow()
    expired_states = []
    
    for state, data in oauth_states.items():
        # Remove states older than 10 minutes
        if (current_time - data['created_at']).seconds > 600:
            expired_states.append(state)
    
    for state in expired_states:
        oauth_states.pop(state, None)
    
    if expired_states:
        logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")

# Test functions
def test_twitter_oauth_flow():
    """Test Twitter OAuth flow (for development)"""
    try:
        test_user_id = 'test_user_oauth'
        
        # Test OAuth initiation
        auth_url = initiate_twitter_oauth(test_user_id)
        print(f"Twitter OAuth URL: {auth_url}")
        
        return True
        
    except Exception as e:
        print(f"Twitter OAuth test failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing OAuth endpoints...")
    
    # Test OAuth URL generation
    twitter_test = test_twitter_oauth_flow()
    
    if twitter_test:
        print("OAuth endpoint tests passed!")
    else:
        print("OAuth endpoint tests failed!")
