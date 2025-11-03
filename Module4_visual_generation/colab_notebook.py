# ============================================
# 🚀 AuroraPress Module 4 - GPU Visual Generator
# Google Colab Edition (for Presentation Demo)
# ============================================

# ---- 1. Setup Environment ----
!pip install -q fastapi uvicorn pyngrok diffusers transformers accelerate pillow torch

import os, io, base64, datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pyngrok import ngrok
from diffusers import StableDiffusionPipeline
from transformers import pipeline
from PIL import Image, ImageDraw, ImageFont

# ---- 2. Banner ----
print("="*80)
print("🪶  AuroraPress Visual Intelligence Module 4 – Powered by GPU (Colab Edition)")
print("🌐  Generating contextual article visuals with Stable Diffusion + BLIP")
print("="*80, "\n")

# ---- 3. Initialize FastAPI ----
app = FastAPI(title="AuroraPress Module 4 (GPU Colab API)")

print("⚙️ Loading models on GPU, please wait 1–2 minutes...")
sd_model = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype="auto"
).to("cuda")
caption_pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
print("✅ Models loaded successfully!\n")

# ---- 4. API Route ----
@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "AI and Journalism Future")
    category = data.get("category", "general")
    
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🎨 Generating image for: {prompt}")
    
    # Enhanced prompt based on category
    if category == "conflict":
        enhanced_prompt = f"serious news photography, {prompt}, photojournalism, realistic, professional"
    elif category == "entertainment":
        enhanced_prompt = f"artistic illustration, {prompt}, creative, vibrant, artistic"
    else:
        enhanced_prompt = f"professional news image, {prompt}, clean, modern"
    
    result = sd_model(enhanced_prompt, num_inference_steps=25, guidance_scale=7.5)
    image = result.images[0]
    
    # Generate caption
    caption = caption_pipe(image)[0]["generated_text"]
    
    # Convert to base64
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    return JSONResponse({
        "success": True,
        "caption": caption,
        "image_base64": image_b64,
        "prompt_used": enhanced_prompt,
        "category": category
    })

# ---- 5. Health Check ----
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AuroraPress Module 4"}

# ---- 6. Expose via Ngrok ----
print("🌐 Setting up public API endpoint...")
public_url = ngrok.connect(8000)
print(f"🌍 Public API Endpoint: {public_url}/generate")
print("Use POST request with JSON { 'prompt': 'Your article title', 'category': 'conflict/entertainment/general' }\n")

# ---- 7. Start Server ----
print("🚀 Starting AuroraPress Module 4 API server...")
print("="*80)
!uvicorn main:app --host 0.0.0.0 --port 8000
