#!/usr/bin/env python3
"""
Startup script for Module 4 - Visual Generation
"""
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Start Module 4 visual generation service."""
    print("🎨 Starting AuroraPress Module 4 - Visual Generation Service")
    print("=" * 60)
    
    # Change to Module 4 directory
    module4_dir = Path(__file__).parent / "Module4_visual_generation"
    os.chdir(module4_dir)
    
    print(f"📁 Working directory: {module4_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Warning: Virtual environment not detected")
    
    # Start the service
    try:
        print("\n🚀 Starting visual generation service on port 8001...")
        print("📡 API will be available at: http://localhost:8001")
        print("📚 API docs at: http://localhost:8001/docs")
        print("\n" + "=" * 60)
        print("Press Ctrl+C to stop the service")
        print("=" * 60 + "\n")
        
        # Run the service
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting service: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())









