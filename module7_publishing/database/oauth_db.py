import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

# Settings fallback
try:
    from config.settings import settings
except ImportError:
    class Settings:
        MONGODB_URL = 'mongodb://localhost:27017/'
        MONGODB_DB = 'AuroraPress'
        ENCRYPTION_KEY = None
    settings = Settings()

# Global database connection - initialized on first use
_client = None
_db = None

def get_database():
    """Get database connection - ensures initialization"""
    global _client, _db
    
    if _client is None:
        try:
            _client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            _db = _client[settings.MONGODB_DB]
            # Test the connection
            _client.admin.command('ping')
            logger.info(f"✓ Connected to MongoDB: {settings.MONGODB_DB}")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            logger.warning("⚠️  Module 7 will work in fallback mode without database")
            # Don't raise, just return None for graceful degradation
            _client = None
            _db = None
    
    return _db

def get_oauth_collection():
    """Get OAuth tokens collection - FIXED to always initialize DB first"""
    db = get_database()  # This ensures _db is set
    if db is None:
        return None
    return db['oauth_tokens']

def store_oauth_token(user_id: str, platform: str, token_data: Dict[str, Any]) -> bool:
    """
    Store or update OAuth token for user
    """
    try:
        collection = get_oauth_collection()
        if collection is None:
            logger.warning("⚠️  Database not available - OAuth token not stored")
            return False
        
        # Calculate expiration
        expires_in = token_data.get('expires_in', 7200)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Prepare token document
        token_document = {
            'user_id': user_id,
            'platform': platform,
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token', ''),
            'token_type': token_data.get('token_type', 'bearer'),
            'scope': token_data.get('scope', ''),
            'expires_at': expires_at,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_valid': True,
            'platform_user_id': token_data.get('platform_user_id', ''),
            'platform_username': token_data.get('platform_username', '')
        }
        
        # Platform-specific fields
        if platform == 'wordpress':
            token_document['site_url'] = token_data.get('site_url', '')
            token_document['username'] = token_data.get('username', '')
        
        # Upsert
        result = collection.replace_one(
            {'user_id': user_id, 'platform': platform},
            token_document,
            upsert=True
        )
        
        logger.info(f"✓ Token stored: {user_id} - {platform}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to store token: {e}", exc_info=True)
        return False

def get_oauth_token(user_id: str, platform: str, include_expired: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get OAuth token for user and platform
    """
    try:
        collection = get_oauth_collection()
        
        query = {
            'user_id': user_id,
            'platform': platform
        }
        
        
        token_doc = collection.find_one(query)
        
        if not token_doc:
            logger.info(f"No token found: {user_id} - {platform}")
            return None
        
        # Check expiration
        expires_at = token_doc.get('expires_at')
        if expires_at and isinstance(expires_at, datetime):
            if expires_at < datetime.utcnow():
                if not include_expired:
                    logger.info(f"Token expired: {user_id} - {platform}")
                    return None
                else:
                    logger.info(f"Returning expired token for refresh: {user_id} - {platform}")
        
        return token_doc
        
    except Exception as e:
        logger.error(f"✗ Error getting token: {e}", exc_info=True)
        return None

def get_user_connections(user_id: str) -> List[Dict[str, Any]]:
    """Get all platform connections for user"""
    try:
        collection = get_oauth_collection()
        
        connections = list(collection.find({
            'user_id': user_id,
            'is_valid': True
        }))
        
        formatted = []
        for conn in connections:
            formatted.append({
                'platform': conn.get('platform'),
                'platform_username': conn.get('platform_username', ''),
                'connected_at': conn.get('created_at', ''),
                'expires_at': conn.get('expires_at', ''),
                'connected': True
            })
        
        return formatted
        
    except Exception as e:
        logger.error(f"✗ Error getting connections: {e}")
        return []

def disconnect_platform(user_id: str, platform: str) -> bool:
    """Disconnect user from platform"""
    try:
        collection = get_oauth_collection()
        
        result = collection.update_one(
            {'user_id': user_id, 'platform': platform},
            {'$set': {'is_valid': False, 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            logger.info(f"✓ Disconnected: {user_id} - {platform}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"✗ Error disconnecting: {e}")
        return False

def store_publishing_record(user_id: str, article_id: str, platform: str, result: Dict[str, Any]) -> bool:
    """Store publishing record"""
    try:
        db = get_database()
        collection = db['publishing_records']
        
        record = {
            'user_id': user_id,
            'article_id': article_id,
            'platform': platform,
            'success': result.get('success', False),
            'published_at': datetime.utcnow(),
            'post_url': result.get('tweet_url') or result.get('post_url', ''),
            'post_id': result.get('tweet_id') or result.get('post_id', ''),
            'error': result.get('error', None)
        }
        
        collection.insert_one(record)
        logger.info(f"✓ Publishing record stored: {user_id} - {platform}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error storing record: {e}")
        return False

def get_user_publications(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's publication history"""
    try:
        db = get_database()
        collection = db['publishing_records']
        
        publications = list(collection.find(
            {'user_id': user_id}
        ).sort('published_at', -1).limit(limit))
        
        for pub in publications:
            pub['_id'] = str(pub['_id'])
        
        return publications
        
    except Exception as e:
        logger.error(f"✗ Error getting publications: {e}")
        return []

def test_database_connection():
    """Test database operations"""
    try:
        db = get_database()
        
        test_data = {
            'access_token': 'test_token_123',
            'expires_in': 3600,
            'platform_user_id': 'test123',
            'platform_username': 'testuser'
        }
        
        store_result = store_oauth_token('test_db_user', 'twitter', test_data)
        if not store_result:
            return False
        
        retrieved = get_oauth_token('test_db_user', 'twitter')
        if not retrieved:
            return False
        
        connections = get_user_connections('test_db_user')
        if len(connections) == 0:
            return False
        
        logger.info("✓ Database test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test FAILED: {e}")
        return False


if __name__ == '__main__':
    success = test_database_connection()
    print(f"Database test: {'PASSED ✓' if success else 'FAILED ✗'}")