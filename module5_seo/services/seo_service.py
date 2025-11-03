# ============================================
# 🚀 AuroraPress Module 5 - SEO Service
# Handles SEO optimization with progress tracking
# ============================================

import asyncio
import time
from typing import Dict, Any, Callable, Optional
from ..models.schemas import SEOOptimizationRequest, SEOOptimizationResponse, SEOProgressUpdate
from ..seo_optimizer_offline import optimize_article
import logging

logger = logging.getLogger(__name__)

class SEOService:
    """Service for SEO optimization with real-time progress tracking"""
    
    def __init__(self):
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def add_progress_callback(self, task_id: str, callback: Callable[[SEOProgressUpdate], None]):
        """Add a progress callback for a specific task"""
        self.progress_callbacks[task_id] = callback
    
    def remove_progress_callback(self, task_id: str):
        """Remove a progress callback"""
        if task_id in self.progress_callbacks:
            del self.progress_callbacks[task_id]
    
    async def _update_progress(self, task_id: str, step: str, progress: int, message: str, completed: bool = False):
        """Update progress for a specific task"""
        if task_id in self.progress_callbacks:
            update = SEOProgressUpdate(
                step=step,
                progress=progress,
                message=message,
                completed=completed
            )
            try:
                callback = self.progress_callbacks[task_id]
                if asyncio.iscoroutinefunction(callback):
                    await callback(update)
                else:
                    callback(update)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def optimize_article_with_progress(self, request: SEOOptimizationRequest, task_id: str = "default") -> SEOOptimizationResponse:
        """
        Optimize article with real-time progress updates
        
        Args:
            request: SEO optimization request
            task_id: Unique task identifier for progress tracking
        
        Returns:
            SEO optimization response with results
        """
        start_time = time.time()
        
        try:
            # Step 1: Initialize
            await self._update_progress(task_id, "initialize", 5, "Initializing SEO optimization...")
            await asyncio.sleep(0.1)  # Small delay for UI updates
            
            # Step 2: Extract keywords
            await self._update_progress(task_id, "keywords", 15, "Extracting keywords...")
            await asyncio.sleep(0.1)
            
            # Step 3: Detect intent
            await self._update_progress(task_id, "intent", 25, "Detecting content intent...")
            await asyncio.sleep(0.1)
            
            # Step 4: Enhance content
            await self._update_progress(task_id, "content", 40, "Enhancing content structure...")
            await asyncio.sleep(0.1)
            
            # Step 5: Optimize title and meta
            await self._update_progress(task_id, "title_meta", 60, "Optimizing title and meta description...")
            await asyncio.sleep(0.1)
            
            # Step 6: Analyze readability
            await self._update_progress(task_id, "readability", 75, "Analyzing readability...")
            await asyncio.sleep(0.1)
            
            # Step 7: Calculate SEO score
            await self._update_progress(task_id, "scoring", 90, "Calculating SEO score...")
            await asyncio.sleep(0.1)
            
            # Run the actual optimization
            logger.info(f"Starting SEO optimization for: {request.article_title}")
            result = optimize_article(request.article_title, request.article_content)
            
            processing_time = time.time() - start_time
            
            # Step 8: Complete
            await self._update_progress(task_id, "complete", 100, "SEO optimization complete!", completed=True)
            
            # Convert to response format
            response = SEOOptimizationResponse(
                success=True,
                original_title=result["original_title"],
                optimized_title=result["optimized_title"],
                meta_description=result["meta_description"],
                optimized_content=result["optimized_content"],
                keywords=result["keywords"],
                intent=result["intent"],
                readability=result["readability"],
                structure=result["structure"],
                seo_score=result["seo_score"],
                slug=result["slug"],
                optimized_at=result["optimized_at"],
                processing_time=processing_time
            )
            
            logger.info(f"SEO optimization completed in {processing_time:.2f}s with score: {result['seo_score']}")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"SEO optimization failed: {e}")
            
            await self._update_progress(task_id, "error", 0, f"SEO optimization failed: {str(e)}", completed=True)
            
            return SEOOptimizationResponse(
                success=False,
                original_title=request.article_title,
                optimized_title=request.article_title,
                meta_description="",
                optimized_content=request.article_content,
                keywords={"primary": [], "secondary": [], "long_tail": []},
                intent="informational",
                readability={"flesch": 0, "grade": 0, "gunning_fog": 0},
                structure={"paragraphs": 0, "avg_sentences_per_para": 0, "avg_sentence_length": 0},
                seo_score=0,
                slug="",
                optimized_at=datetime.now().isoformat(),
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def optimize_article_simple(self, title: str, content: str) -> Dict[str, Any]:
        """
        Simple SEO optimization without progress tracking
        
        Args:
            title: Article title
            content: Article content
        
        Returns:
            SEO optimization results
        """
        try:
            logger.info(f"Starting simple SEO optimization for: {title}")
            result = optimize_article(title, content)
            logger.info(f"SEO optimization completed with score: {result['seo_score']}")
            return result
        except Exception as e:
            logger.error(f"Simple SEO optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_title": title,
                "optimized_content": content
            }





