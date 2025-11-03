# 🚀 AuroraPress Module 4 - Google Colab Setup Guide

## 🎯 **Quick Start (5 minutes)**

### **Step 1: Open Google Colab**
1. Go to [Google Colab](https://colab.research.google.com/)
2. Sign in with your Google account
3. Click "New Notebook"

### **Step 2: Copy & Paste Code**
1. Copy the entire content from `colab_notebook.py`
2. Paste it into the first cell of your Colab notebook
3. Click the "Run" button (▶️)

### **Step 3: Wait for Setup**
- Colab will install dependencies (1-2 minutes)
- Models will load on GPU (1-2 minutes)
- You'll see: `✅ Models loaded successfully!`

### **Step 4: Get Your API URL**
- Look for: `🌍 Public API Endpoint: https://abc123.ngrok.io/generate`
- Copy this URL - you'll need it for the backend

### **Step 5: Update Backend Configuration**
1. Open `Module4_visual_generation/colab_config.py`
2. Replace `"https://your-ngrok-url.ngrok.io"` with your actual ngrok URL
3. Save the file

### **Step 6: Test the Integration**
1. Restart your AuroraPress backend
2. Generate a new article
3. Check if real AI images appear!

---

## 🔧 **Configuration Details**

### **Backend Configuration**
```python
# In colab_config.py
COLAB_API_URL = "https://your-actual-ngrok-url.ngrok.io"
```

### **Environment Variables (Optional)**
```bash
# Add to your .env file
COLAB_API_URL=https://your-actual-ngrok-url.ngrok.io
```

---

## 🎨 **What You'll Get**

### **Real AI Images:**
- **High quality** Stable Diffusion v1.5 generated images
- **Contextual relevance** - images match article content
- **Professional captions** - AI-generated descriptions
- **Fast generation** - 30-60 seconds per image

### **Category-Specific Styles:**
- **Conflict/Politics**: Serious, photojournalistic style
- **Entertainment**: Artistic, creative illustrations
- **General**: Clean, professional news images

### **Fallback System:**
- If Colab is down → Enhanced mock images
- If generation fails → Graceful degradation
- Always have visuals to display

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. "Colab not available"**
- Check if your Colab notebook is still running
- Verify the ngrok URL is correct
- Test the health endpoint: `https://your-url.ngrok.io/health`

#### **2. "Generation failed"**
- Check Colab logs for errors
- Verify GPU is enabled in Colab
- Try restarting the Colab notebook

#### **3. "Timeout errors"**
- Increase timeout in `colab_config.py`
- Check your internet connection
- Verify Colab is responsive

### **Debug Commands:**
```bash
# Test Colab connection
curl https://your-ngrok-url.ngrok.io/health

# Test image generation
curl -X POST https://your-ngrok-url.ngrok.io/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test article", "category": "general"}'
```

---

## 🔄 **Maintenance**

### **Daily:**
- Keep Colab notebook running during demos
- Check ngrok URL hasn't changed

### **Weekly:**
- Restart Colab notebook to refresh models
- Update ngrok URL if needed

### **Monthly:**
- Consider upgrading to paid Colab for stability
- Or migrate to Replicate/Fal.ai for production

---

## 🎯 **Production Recommendations**

### **For Demo/Presentation:**
- Use this Colab setup (free, fast, impressive)

### **For Production:**
- Migrate to Replicate API or Fal.ai
- Set up permanent GPU infrastructure
- Implement proper error handling and monitoring

---

## 📞 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all URLs are correct
3. Check Colab logs for specific errors
4. Ensure your backend is properly configured

**Happy generating! 🎨✨**








