#!/usr/bin/env python3
"""
🚀 AuroraPress - Colab Integration Quick Start
This script helps you set up the Colab integration quickly
"""

import os
import sys
import asyncio
import subprocess

def print_banner():
    """Print the startup banner"""
    print("=" * 80)
    print("🪶  AuroraPress - Colab Integration Quick Start")
    print("🌐  Setting up GPU-powered visual generation")
    print("=" * 80)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import aiohttp
        print("   ✅ aiohttp installed")
    except ImportError:
        print("   ❌ aiohttp not found - installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], check=True)
        print("   ✅ aiohttp installed")
    
    try:
        import pyngrok
        print("   ✅ pyngrok installed")
    except ImportError:
        print("   ❌ pyngrok not found - installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyngrok"], check=True)
        print("   ✅ pyngrok installed")
    
    print("   ✅ All dependencies ready!")
    print()

def show_colab_instructions():
    """Show instructions for setting up Colab"""
    print("📋 Next Steps:")
    print("   1. Open Google Colab: https://colab.research.google.com/")
    print("   2. Create a new notebook")
    print("   3. Copy the code from: Module4_visual_generation/colab_notebook.py")
    print("   4. Paste and run it in Colab")
    print("   5. Wait for the ngrok URL (e.g., https://abc123.ngrok.io)")
    print("   6. Copy that URL and update colab_config.py")
    print()

def update_config():
    """Help user update the configuration"""
    print("⚙️ Configuration Update:")
    print("   Open: Module4_visual_generation/colab_config.py")
    print("   Replace: 'https://your-ngrok-url.ngrok.io'")
    print("   With: Your actual ngrok URL from Colab")
    print()

def test_integration():
    """Test the integration"""
    print("🧪 Testing Integration:")
    print("   Run: python Module4_visual_generation/test_colab_integration.py")
    print("   This will test if everything is working correctly")
    print()

def show_usage():
    """Show how to use the integration"""
    print("🚀 Usage:")
    print("   1. Start your AuroraPress backend: python main.py")
    print("   2. Generate a new article")
    print("   3. Check if real AI images appear!")
    print()

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    check_dependencies()
    
    # Show instructions
    show_colab_instructions()
    update_config()
    test_integration()
    show_usage()
    
    print("🎉 Setup complete! Follow the steps above to get started.")
    print("   Need help? Check: Module4_visual_generation/COLAB_SETUP.md")

if __name__ == "__main__":
    main()








