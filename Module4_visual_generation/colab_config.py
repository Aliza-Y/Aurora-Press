# ============================================
# 🚀 AuroraPress Module 4 - Colab Configuration
# ============================================

import os
from typing import Optional

class ColabConfig:
    """Configuration for Google Colab integration"""
    
    # Colab API endpoint (update this with your ngrok URL)
    COLAB_API_URL: str = os.getenv("COLAB_API_URL", "https://eee305241163.ngrok-free.app")
    
    # API endpoints
    GENERATE_ENDPOINT: str = f"{COLAB_API_URL}/generate"
    HEALTH_ENDPOINT: str = f"{COLAB_API_URL}/health"
    
    # Request settings
    TIMEOUT_SECONDS: int = 180  # 3 minutes timeout
    MAX_RETRIES: int = 2
    
    # Image settings
    DEFAULT_CATEGORY: str = "general"
    FALLBACK_TO_MOCK: bool = True
    
    @classmethod
    def update_url(cls, new_url: str):
        """Update the Colab API URL"""
        cls.COLAB_API_URL = new_url
        cls.GENERATE_ENDPOINT = f"{new_url}/generate"
        cls.HEALTH_ENDPOINT = f"{new_url}/health"
        print(f"✅ Updated Colab API URL to: {new_url}")
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test if Colab endpoint is reachable"""
        import requests
        try:
            response = requests.get(cls.HEALTH_ENDPOINT, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Colab connection test failed: {e}")
            return False

# Global config instance
colab_config = ColabConfig()
