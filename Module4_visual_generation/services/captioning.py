import re
from typing import List, Dict, Any
from ..models.schemas import ImageStyle, ImageType
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CaptionGenerationService:
    """Service for generating captions for generated images."""
    
    def __init__(self):
        self.logger = logger
    
    def generate_caption(
        self, 
        article_title: str, 
        article_content: str, 
        image_style: ImageStyle,
        image_type: ImageType,
        keywords: List[str],
        prompt_used: str
    ) -> str:
        """Generate a relevant caption for the image."""
        
        try:
            # Extract key information from the article
            key_phrases = self._extract_key_phrases(article_title, article_content, keywords)
            
            # Generate caption based on image type and style
            if image_type == ImageType.HEADER:
                caption = self._generate_header_caption(article_title, key_phrases, image_style)
            else:
                caption = self._generate_inline_caption(article_content, key_phrases, image_style)
            
            # Clean and format the caption
            caption = self._clean_caption(caption)
            
            self.logger.info(f"Generated caption for {image_type.value} image: {caption[:50]}...")
            return caption
            
        except Exception as e:
            self.logger.error(f"Error generating caption: {str(e)}")
            # Fallback caption
            return f"Image related to {article_title}"
    
    def _extract_key_phrases(self, title: str, content: str, keywords: List[str]) -> List[str]:
        """Extract key phrases from article content."""
        key_phrases = []
        
        # Add keywords
        key_phrases.extend(keywords[:3])  # Limit to top 3 keywords
        
        # Extract important words from title
        title_words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+\b', title)
        key_phrases.extend(title_words[:2])
        
        # Extract key phrases from content (first paragraph)
        first_paragraph = content.split('\n')[0] if content else ""
        important_words = re.findall(r'\b[A-Z][a-z]+\b', first_paragraph)
        key_phrases.extend(important_words[:2])
        
        # Remove duplicates and limit length
        unique_phrases = list(dict.fromkeys(key_phrases))[:5]
        return unique_phrases
    
    def _generate_header_caption(self, title: str, key_phrases: List[str], style: ImageStyle) -> str:
        """Generate caption for header image."""
        if style == ImageStyle.REALISTIC:
            return f"News image showing {', '.join(key_phrases[:2])} related to {title}"
        else:
            return f"Artistic illustration representing {', '.join(key_phrases[:2])} in {title}"
    
    def _generate_inline_caption(self, content: str, key_phrases: List[str], style: ImageStyle) -> str:
        """Generate caption for inline image."""
        if style == ImageStyle.REALISTIC:
            return f"Photo depicting {', '.join(key_phrases[:2])} as mentioned in the article"
        else:
            return f"Creative visualization of {', '.join(key_phrases[:2])} concept"
    
    def _clean_caption(self, caption: str) -> str:
        """Clean and format the caption."""
        # Remove extra spaces and newlines
        caption = re.sub(r'\s+', ' ', caption.strip())
        
        # Ensure proper capitalization
        caption = caption[0].upper() + caption[1:] if caption else ""
        
        # Limit length
        if len(caption) > 150:
            caption = caption[:147] + "..."
        
        return caption
    
    def generate_multiple_captions(
        self, 
        article_title: str, 
        article_content: str, 
        image_styles: List[ImageStyle],
        image_types: List[ImageType],
        keywords: List[str],
        prompts_used: List[str]
    ) -> List[str]:
        """Generate multiple captions for multiple images."""
        captions = []
        
        for i, (style, img_type, prompt) in enumerate(zip(image_styles, image_types, prompts_used)):
            caption = self.generate_caption(
                article_title, 
                article_content, 
                style, 
                img_type, 
                keywords, 
                prompt
            )
            captions.append(caption)
        
        return captions
