import datetime
import sys
from pathlib import Path

from database import oauth_db
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, Request, Query, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from api.oauth_endpoints import (
    initiate_twitter_oauth, handle_twitter_oauth_callback,
    connect_wordpress_site, validate_user_token,
    get_user_platform_info, cleanup_oauth_states
)
from database.oauth_db import get_user_connections, disconnect_platform

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AuroraPress OAuth API",
    description="OAuth authentication for multi-platform publishing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TwitterConnectRequest(BaseModel):
    user_id: str

class LinkedInConnectRequest(BaseModel):
    user_id: str

class WordPressConnectRequest(BaseModel):
    user_id: str
    site_url: str
    username: str
    password: str

class DisconnectRequest(BaseModel):
    user_id: str
    platform: str

class SchedulePublicationRequest(BaseModel):
    user_id: str
    article_data: dict
    target_platforms: List[str]
    scheduled_time: str

# OAuth initiation endpoints
@app.post("/auth/twitter/connect")
async def connect_twitter(request: TwitterConnectRequest):
    """Initiate Twitter OAuth connection"""
    try:
        auth_url = initiate_twitter_oauth(request.user_id)
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Redirect user to auth_url to complete Twitter connection"
        }
    except Exception as e:
        logger.error(f"Twitter connection initiation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/twitter/callback")
async def twitter_callback(
    code: str = Query(..., description="Authorization code from Twitter"),
    state: str = Query(..., description="OAuth state parameter")
):
    """Handle Twitter OAuth callback"""
    try:
        result = handle_twitter_oauth_callback(code, state)
        
        if result['success']:
            # Return success page or redirect to frontend
            return HTMLResponse(f"""
            <html>
                <head><title>Twitter Connected</title></head>
                <body>
                    <h2>Twitter Account Connected Successfully!</h2>
                    <p>Username: @{result['platform_username']}</p>
                    <p>You can now close this window and return to AuroraPress.</p>
                    <script>
                        setTimeout(function() {{
                            window.close();
                        }}, 3000);
                    </script>
                </body>
            </html>
            """)
        else:
            raise HTTPException(status_code=400, detail="Twitter connection failed")
            
    except Exception as e:
        logger.error(f"Twitter callback failed: {e}")
        return HTMLResponse(f"""
        <html>
            <head><title>Connection Failed</title></head>
            <body>
                <h2>Twitter Connection Failed</h2>
                <p>Error: {str(e)}</p>
                <p>Please try again or contact support.</p>
            </body>
        </html>
        """)

# Scheduling endpoint
@app.post("/publish/schedule")
async def schedule_publication(request: SchedulePublicationRequest):
    """Schedule article for future publication"""
    try:
        from module7_publishing.tasks.scheduling_tasks import schedule_article_publication
        
        result = schedule_article_publication.delay(
            request.user_id,
            request.article_data,
            request.target_platforms,
            request.scheduled_time
        )
        
        return result.get(timeout=15)
    except Exception as e:
        logger.error(f"Scheduling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/publish/schedule/{scheduled_id}")
async def cancel_scheduled_publication(scheduled_id: str, user_id: str = Query(...)):
    """Cancel a scheduled post"""
    try:
        from module7_publishing.tasks.scheduling_tasks import cancel_scheduled_post
        result = cancel_scheduled_post.delay(user_id, scheduled_id)
        return result.get(timeout=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/publish/scheduled/{user_id}")
async def get_scheduled_posts(user_id: str, status: str = Query(None)):
    """Get user's scheduled posts"""
    try:
        from module7_publishing.tasks.scheduling_tasks import get_user_scheduled_posts
        result = get_user_scheduled_posts.delay(user_id, status)
        return result.get(timeout=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/wordpress/connect")
async def connect_wordpress(request: WordPressConnectRequest):
    """Connect WordPress site using credentials"""
    try:
        result = connect_wordpress_site(
            request.user_id, 
            request.site_url, 
            request.username, 
            request.password
        )
        
        if result['success']:
            return {
                "success": True,
                "platform": "wordpress",
                "site_url": result['site_url'],
                "username": result['platform_username'],
                "message": "WordPress site connected successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        logger.error(f"WordPress connection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User connection management endpoints
@app.get("/auth/connections/{user_id}")
async def get_user_platform_connections(user_id: str):
    """Get all platform connections for a user"""
    try:
        connections = get_user_connections(user_id)
        
        # Add connection status and details
        detailed_connections = []
        for connection in connections:
            platform_info = get_user_platform_info(user_id, connection['platform'])
            if platform_info:
                detailed_connections.append(platform_info)
        
        return {
            "user_id": user_id,
            "connections": detailed_connections,
            "total_connections": len(detailed_connections)
        }
        
    except Exception as e:
        logger.error(f"Error getting user connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/disconnect")
async def disconnect_platform_endpoint(request: DisconnectRequest):
    """Disconnect user from platform"""
    try:
        result = disconnect_platform(request.user_id, request.platform)
        
        if result:
            return {
                "success": True,
                "user_id": request.user_id,
                "platform": request.platform,
                "message": f"Disconnected from {request.platform} successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Disconnection failed")
            
    except Exception as e:
        logger.error(f"Platform disconnection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Platform status endpoints
@app.get("/auth/status/{user_id}/{platform}")
async def check_platform_status(user_id: str, platform: str):
    """Check connection status for specific platform"""
    try:
        is_connected = validate_user_token(user_id, platform)
        platform_info = get_user_platform_info(user_id, platform)
        
        return {
            "user_id": user_id,
            "platform": platform,
            "connected": is_connected,
            "details": platform_info
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check and utility endpoints
@app.get("/auth/health")
async def auth_health_check():
    """Health check for OAuth service"""
    return {
        "status": "healthy",
        "service": "AuroraPress OAuth API",
        "version": "1.0.0",
        "timestamp": "2024-11-22T10:00:00Z"
    }

@app.post("/auth/cleanup")
async def cleanup_oauth_states_endpoint():
    """Clean up expired OAuth states"""
    try:
        cleanup_oauth_states()
        return {"success": True, "message": "OAuth states cleaned up"}
    except Exception as e:
        logger.error(f"OAuth cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Frontend helper endpoints
@app.get("/auth/platforms")
async def get_available_platforms():
    """Get list of available platforms for connection"""
    return {
        "platforms": [
            {
                "name": "twitter",
                "display_name": "Twitter/X",
                "oauth_type": "oauth2_pkce",
                "description": "Connect your Twitter account to share articles"
            },
            {
                "name": "linkedin", 
                "display_name": "LinkedIn",
                "oauth_type": "oauth2",
                "description": "Connect your LinkedIn profile to share professional content"
            },
            {
                "name": "wordpress",
                "display_name": "WordPress",
                "oauth_type": "credentials",
                "description": "Connect your WordPress site to publish articles"
            }
        ]
    }

@app.get("/auth/debug/callback")
async def debug_callback(code: str = None, state: str = None, error: str = None):
    """Debug endpoint to see what's happening with Twitter callback"""
    
    debug_info = {
        "callback_received": True,
        "timestamp": "2024-11-22T15:00:00Z",  # Static timestamp to avoid import issues
        "parameters": {
            "code": code[:20] + "..." if code else None,
            "state": state,
            "error": error
        },
        "imports_status": {},
        "database_status": "unknown"
    }
    
    # Test imports
    try:
        from api.oauth_endpoints import handle_twitter_oauth_callback
        debug_info["imports_status"]["oauth_endpoints"] = "success"
    except Exception as e:
        debug_info["imports_status"]["oauth_endpoints"] = f"failed: {str(e)}"
    
    try:
        from database.oauth_db import store_oauth_token
        debug_info["imports_status"]["oauth_db"] = "success" 
    except Exception as e:
        debug_info["imports_status"]["oauth_db"] = f"failed: {str(e)}"
    
    try:
        from config.settings import settings
        debug_info["imports_status"]["settings"] = "success"
        debug_info["twitter_config"] = {
            "client_id_set": bool(getattr(settings, 'TWITTER_CLIENT_ID', '')),
            "client_secret_set": bool(getattr(settings, 'TWITTER_CLIENT_SECRET', ''))
        }
    except Exception as e:
        debug_info["imports_status"]["settings"] = f"failed: {str(e)}"
    
    return debug_info

# Also add a simplified callback for testing
@app.get("/auth/twitter/callback-simple")
async def twitter_callback_simple(code: str = None, state: str = None, error: str = None):
    """Simplified callback for debugging"""
    
    if error:
        return HTMLResponse(f"""
        <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h2>OAuth Error Received</h2>
                <p>Error: {error}</p>
                <p>This means Twitter rejected the authorization.</p>
            </body>
        </html>
        """)
    
    if not code or not state:
        return HTMLResponse(f"""
        <html>
            <head><title>Missing Parameters</title></head>
            <body>
                <h2>Missing OAuth Parameters</h2>
                <p>Code: {'Present' if code else 'Missing'}</p>
                <p>State: {'Present' if state else 'Missing'}</p>
                <p>Check your Twitter app callback URL configuration.</p>
            </body>
        </html>
        """)
    
    return HTMLResponse(f"""
    <html>
        <head><title>Callback Test</title></head>
        <body>
            <h2>OAuth Callback Received Successfully!</h2>
            <p>Code: {code[:20]}...</p>
            <p>State: {state}</p>
            <p>This proves the callback is working. Now we need to test token exchange.</p>
        </body>
    </html>
    """)

@app.get("/auth/test-env")
async def test_env():
    import os
    return {
        "twitter_client_id": os.getenv('TWITTER_CLIENT_ID', 'NOT_SET')[:10] + "..." if os.getenv('TWITTER_CLIENT_ID') else 'NOT_SET',
        "twitter_client_secret": "SET" if os.getenv('TWITTER_CLIENT_SECRET') else 'NOT_SET',
        "env_file_path": str(Path.cwd() / '.env'),
        "env_file_exists": (Path.cwd() / '.env').exists()
    }

@app.get("/auth/debug/oauth-states")
async def debug_oauth_states_endpoint():
    """Debug OAuth states"""
    try:
        from api.oauth_endpoints import debug_oauth_states
        return debug_oauth_states()
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/auth/test-database")
async def test_database():
       from database.oauth_db import test_database_connection
       success = test_database_connection()
       return {"database_test": "PASSED" if success else "FAILED"}

@app.get("/auth/debug-env-detailed")
async def debug_env_detailed():
    import os
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / '.env'
    
    debug_info = {
        "current_directory": str(Path.cwd()),
        "base_directory": str(base_dir),
        "env_file_path": str(env_file),
        "env_file_exists": env_file.exists(),
        "raw_env_vars": {
            "TWITTER_CLIENT_ID": os.getenv('TWITTER_CLIENT_ID', 'NOT_FOUND'),
            "TWITTER_CLIENT_SECRET": os.getenv('TWITTER_CLIENT_SECRET', 'NOT_FOUND')
        }
    }
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            debug_info["env_file_preview"] = content[:500]  # First 500 characters
    
    return debug_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)