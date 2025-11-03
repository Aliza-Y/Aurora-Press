"""
Configuration settings for Module 7 - Publishing & Distribution
Updated to explicitly load .env file
"""

import os
from typing import Dict, List, Optional
from pathlib import Path

# Load .env file explicitly
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Load .env file
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

class Settings:
    """Centralized configuration management"""
    
    # Redis Configuration
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # MongoDB Configuration (reuse existing connection)
    MONGODB_URL: str = os.getenv('MONGO_URI', os.getenv('MONGODB_URL', 'mongodb://localhost:27017/'))
    MONGODB_DB: str = os.getenv('DATABASE_NAME', 'aurorapress')
    
    # Debug MongoDB connection
    @classmethod
    def debug_mongodb_config(cls):
        print(f"=== Module 7 MongoDB Debug ===")
        print(f"MONGO_URI from env: {os.getenv('MONGO_URI', 'NOT_SET')}")
        print(f"MONGODB_URL from env: {os.getenv('MONGODB_URL', 'NOT_SET')}")
        print(f"Final MONGODB_URL: {cls.MONGODB_URL}")
        print(f"Final MONGODB_DB: {cls.MONGODB_DB}")
    
    # FastAPI Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8002'))
    
    # Twitter OAuth 2.0 Configuration
    TWITTER_CLIENT_ID: str = os.getenv('TWITTER_CLIENT_ID', '')
    TWITTER_CLIENT_SECRET: str = os.getenv('TWITTER_CLIENT_SECRET', '')
    TWITTER_BEARER_TOKEN: str = os.getenv('TWITTER_BEARER_TOKEN', '')
    
    # LinkedIn OAuth 2.0 Configuration
    LINKEDIN_CLIENT_ID: str = os.getenv('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET: str = os.getenv('LINKEDIN_CLIENT_SECRET', '')
    
    # WordPress Configuration
    WORDPRESS_URL: str = os.getenv('WORDPRESS_URL', '')
    WORDPRESS_USERNAME: str = os.getenv('WORDPRESS_USERNAME', '')
    WORDPRESS_PASSWORD: str = os.getenv('WORDPRESS_PASSWORD', '')
    WORDPRESS_APP_PASSWORD: str = os.getenv('WORDPRESS_APP_PASSWORD', '')
    
    @classmethod
    def debug_env_loading(cls):
        """Debug environment variable loading"""
        print("=== Environment Debug ===")
        print(f"Base directory: {BASE_DIR}")
        print(f"Env file path: {env_path}")
        print(f"Env file exists: {env_path.exists()}")
        print(f"Twitter Client ID loaded: {'SET' if cls.TWITTER_CLIENT_ID else 'NOT_SET'}")
        print(f"Twitter Client Secret loaded: {'SET' if cls.TWITTER_CLIENT_SECRET else 'NOT_SET'}")
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
                has_twitter_id = 'TWITTER_CLIENT_ID=' in content
                has_twitter_secret = 'TWITTER_CLIENT_SECRET=' in content
                print(f"Env file contains TWITTER_CLIENT_ID: {has_twitter_id}")
                print(f"Env file contains TWITTER_CLIENT_SECRET: {has_twitter_secret}")

# Initialize settings instance
settings = Settings()

# Debug on import (remove this after fixing)
if __name__ != '__main__':
    settings.debug_env_loading()
    settings.debug_mongodb_config()