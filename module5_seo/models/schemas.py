# ============================================
# 🚀 AuroraPress Module 5 - SEO Schemas
# ============================================

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class SEOKeywords(BaseModel):
    primary: List[str]
    secondary: List[str]
    long_tail: List[str]

class SEOReadability(BaseModel):
    flesch: float
    grade: float
    gunning_fog: float

class SEOStructure(BaseModel):
    paragraphs: int
    avg_sentences_per_para: float
    avg_sentence_length: float

class SEOOptimizationRequest(BaseModel):
    article_title: str
    article_content: str
    article_summary: Optional[str] = None
    category: Optional[str] = "general"

class SEOOptimizationResponse(BaseModel):
    success: bool
    original_title: str
    optimized_title: str
    meta_description: str
    optimized_content: str
    keywords: SEOKeywords
    intent: str
    readability: SEOReadability
    structure: SEOStructure
    seo_score: float
    slug: str
    optimized_at: str
    processing_time: float
    error_message: Optional[str] = None

class SEOProgressUpdate(BaseModel):
    step: str
    progress: int  # 0-100
    message: str
    completed: bool = False





