import base64
import io
import gc
import psutil
import time
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from ..models.schemas import ImageStyle, ImageType, GeneratedImage
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ImageGenerationService:
    """Service for generating images using Stable Diffusion."""
    
    def __init__(self):
        self.logger = logger
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.memory_threshold = 8 * 1024 * 1024 * 1024  # 8GB threshold
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the Stable Diffusion pipeline with memory optimization."""
        try:
            self.logger.info(f"Initializing Stable Diffusion on {self.device}")
            
            # Use a smaller, more memory-efficient model
            model_id = "runwayml/stable-diffusion-v1-5"
            
            # Initialize pipeline with memory optimizations
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float32,  # Always use float32 for CPU
                use_safetensors=True
            )
            
            # Use memory-efficient scheduler
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory efficient attention if available
            if hasattr(self.pipeline, 'enable_memory_efficient_attention'):
                self.pipeline.enable_memory_efficient_attention()
            
            # Enable CPU offloading for memory efficiency (only on CPU)
            if self.device == "cpu" and hasattr(self.pipeline, 'enable_sequential_cpu_offload'):
                self.pipeline.enable_sequential_cpu_offload()
            
            self.logger.info("Stable Diffusion pipeline initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Stable Diffusion pipeline: {str(e)}")
            # Try a simpler initialization for CPU
            try:
                self.logger.info("Trying simplified CPU-only initialization...")
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float32,
                    use_safetensors=True
                )
                self.pipeline = self.pipeline.to(self.device)
                self.logger.info("Simplified Stable Diffusion pipeline initialized successfully")
            except Exception as e2:
                self.logger.error(f"Simplified initialization also failed: {str(e2)}")
                self.pipeline = None
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage."""
        memory_info = psutil.virtual_memory()
        return {
            "total": memory_info.total,
            "available": memory_info.available,
            "used": memory_info.used,
            "percentage": memory_info.percent,
            "is_low_memory": memory_info.available < self.memory_threshold
        }
    
    def generate_images(
        self,
        article_title: str,
        article_content: str,
        article_summary: str,
        category: str,
        keywords: List[str],
        max_images: int = 2,
        preferred_style: Optional[ImageStyle] = None
    ) -> List[GeneratedImage]:
        """Generate images for the article."""
        
        if not self.pipeline:
            self.logger.error("Pipeline not initialized")
            return []
        
        # Check memory before generation
        memory_info = self.check_memory_usage()
        if memory_info["is_low_memory"]:
            self.logger.warning("Low memory detected, reducing image count")
            max_images = 1
        
        # Determine image styles and types
        image_configs = self._determine_image_configs(
            category, preferred_style, max_images, memory_info
        )
        
        generated_images = []
        
        try:
            for i, config in enumerate(image_configs):
                self.logger.info(f"Generating image {i+1}/{len(image_configs)}")
                
                # Generate prompt
                prompt = self._create_prompt(
                    article_title, article_content, article_summary,
                    keywords, config["style"], config["type"]
                )
                
                # Generate image
                image = self._generate_single_image(prompt, config["style"])
                
                if image:
                    # Convert to base64
                    image_data = self._image_to_base64(image)
                    
                    # Create GeneratedImage object
                    generated_image = GeneratedImage(
                        image_id=f"img_{int(time.time())}_{i}",
                        image_type=config["type"],
                        image_data=image_data,
                        caption="",  # Will be filled by captioning service
                        style=config["style"],
                        prompt_used=prompt,
                        generation_metadata={
                            "generation_time": time.time(),
                            "memory_usage": memory_info,
                            "device": self.device
                        }
                    )
                    
                    generated_images.append(generated_image)
                    
                    # Clean up memory
                    del image
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                
        except Exception as e:
            self.logger.error(f"Error generating images: {str(e)}")
        
        return generated_images
    
    def _determine_image_configs(
        self, 
        category: str, 
        preferred_style: Optional[ImageStyle], 
        max_images: int,
        memory_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Determine image configurations based on category and memory."""
        configs = []
        
        # Determine style based on category
        if preferred_style:
            style = preferred_style
        else:
            artistic_categories = ["entertainment", "health", "sports", "lifestyle", "arts"]
            style = ImageStyle.ARTISTIC if category.lower() in artistic_categories else ImageStyle.REALISTIC
        
        # Always generate header image
        configs.append({
            "type": ImageType.HEADER,
            "style": style
        })
        
        # Add inline image if memory allows and max_images > 1
        if max_images > 1 and not memory_info["is_low_memory"]:
            configs.append({
                "type": ImageType.INLINE,
                "style": style
            })
        
        return configs
    
    def _create_prompt(
        self, 
        title: str, 
        content: str, 
        summary: str,
        keywords: List[str],
        style: ImageStyle,
        image_type: ImageType
    ) -> str:
        """Create a prompt for image generation."""
        
        # Base prompt components
        if style == ImageStyle.REALISTIC:
            base_style = "professional news photography, high quality, realistic, photojournalism style"
        else:
            base_style = "artistic illustration, creative, stylized, digital art, vibrant colors"
        
        # Extract key concepts
        key_concepts = keywords[:3] if keywords else []
        if not key_concepts:
            # Extract from title
            key_concepts = [word for word in title.split() if len(word) > 3][:3]
        
        # Create context-specific prompt
        if image_type == ImageType.HEADER:
            context = f"header image for news article about {', '.join(key_concepts)}"
        else:
            context = f"illustration related to {', '.join(key_concepts)}"
        
        # Combine into final prompt
        prompt = f"{context}, {base_style}, {', '.join(key_concepts)}"
        
        # Add quality modifiers
        prompt += ", high resolution, detailed, professional"
        
        # Add negative prompt for better results
        negative_prompt = "blurry, low quality, distorted, amateur, cartoon, anime"
        
        return prompt, negative_prompt
    
    def _generate_single_image(self, prompt: str, style: ImageStyle) -> Optional[Image.Image]:
        """Generate a single image using the pipeline."""
        try:
            prompt_text, negative_prompt = prompt if isinstance(prompt, tuple) else (prompt, "")
            
            # Generate image with optimized settings
            result = self.pipeline(
                prompt=prompt_text,
                negative_prompt=negative_prompt,
                num_inference_steps=20,  # Reduced for speed
                guidance_scale=7.5,
                width=512,  # Smaller size for memory efficiency
                height=512,
                num_images_per_prompt=1
            )
            
            return result.images[0]
            
        except Exception as e:
            self.logger.error(f"Error generating single image: {str(e)}")
            return None
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        try:
            # Resize if too large to save memory
            if image.width > 1024 or image.height > 1024:
                image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            # Encode to base64
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_data
            
        except Exception as e:
            self.logger.error(f"Error converting image to base64: {str(e)}")
            return ""
    
    def cleanup(self):
        """Clean up resources."""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("Image generation service cleaned up")
