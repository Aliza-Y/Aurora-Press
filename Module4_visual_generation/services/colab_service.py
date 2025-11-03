# ============================================
# 🚀 AuroraPress Module 4 - Colab Service
# Handles communication with Google Colab GPU endpoint
# ============================================

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from ..colab_config import colab_config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ColabService:
    """Service for communicating with Google Colab GPU endpoint"""
    
    def __init__(self):
        self.config = colab_config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.TIMEOUT_SECONDS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_connection(self) -> bool:
        """Test if Colab endpoint is reachable"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10)
                )
            
            async with self.session.get(self.config.HEALTH_ENDPOINT) as response:
                if response.status == 200:
                    logger.info("✅ Colab endpoint is reachable")
                    return True
                else:
                    logger.warning(f"⚠️ Colab endpoint returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Colab connection test failed: {e}")
            return False
        finally:
            if self.session:
                await self.session.close()
                self.session = None
    
    async def generate_image(self, prompt: str, category: str = "general") -> Dict[str, Any]:
        """
        Generate image using Colab GPU endpoint
        
        Args:
            prompt: Article headline or topic
            category: Content category (conflict, entertainment, general)
        
        Returns:
            Dict containing image data and metadata
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.TIMEOUT_SECONDS)
            )
        
        payload = {
            "prompt": prompt,
            "category": category
        }
        
        logger.info(f"🎨 Requesting image generation from Colab: {prompt[:50]}...")
        
        try:
            async with self.session.post(
                self.config.GENERATE_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        logger.info("✅ Image generated successfully from Colab")
                        return {
                            "success": True,
                            "image_data": f"data:image/png;base64,{data['image_base64']}",
                            "caption": data.get("caption", ""),
                            "prompt_used": data.get("prompt_used", prompt),
                            "category": data.get("category", category),
                            "source": "colab_gpu"
                        }
                    else:
                        logger.error("❌ Colab returned unsuccessful response")
                        return self._create_fallback_response(prompt, category)
                else:
                    logger.error(f"❌ Colab API error: {response.status}")
                    return self._create_fallback_response(prompt, category)
                    
        except asyncio.TimeoutError:
            logger.error("⏰ Colab request timed out")
            return self._create_fallback_response(prompt, category)
        except Exception as e:
            logger.error(f"❌ Colab request failed: {e}")
            return self._create_fallback_response(prompt, category)
    
    def _create_fallback_response(self, prompt: str, category: str) -> Dict[str, Any]:
        """Create fallback response when Colab fails"""
        logger.info("🔄 Falling back to mock image generation")
        
        # Import mock service for fallback
        from .visual_generation import VisualGenerationService
        
        # Create mock visual generation service
        mock_service = VisualGenerationService()
        
        # Generate mock image
        mock_result = mock_service._generate_mock_image(prompt, category)
        
        return {
            "success": True,
            "image_data": mock_result["image_data"],
            "caption": mock_result.get("caption", ""),
            "prompt_used": prompt,
            "category": category,
            "source": "mock_fallback"
        }
    
    async def generate_multiple_images(self, prompt: str, category: str = "general", count: int = 2) -> Dict[str, Any]:
        """
        Generate multiple images for an article
        
        Args:
            prompt: Article headline or topic
            category: Content category
            count: Number of images to generate
        
        Returns:
            Dict containing multiple images
        """
        images = []
        
        for i in range(count):
            # Add variation to prompt for different images
            if i == 0:
                varied_prompt = f"header image, {prompt}"
            else:
                varied_prompt = f"inline image, {prompt}, different angle"
            
            result = await self.generate_image(varied_prompt, category)
            if result["success"]:
                images.append({
                    "image_data": result["image_data"],
                    "caption": result["caption"],
                    "image_type": "header" if i == 0 else "inline",
                    "style": "realistic" if category == "conflict" else "artistic"
                })
        
        return {
            "success": True,
            "images": images,
            "total_images": len(images),
            "source": "colab_gpu"
        }
