import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "aurorapress")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "aurorapress/module9_interview_ai/uploads")
VOSK_MODEL_DIR = os.getenv("VOSK_MODEL_DIR", "")

# Whisper settings (force Whisper by leaving VOSK empty)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "")   # empty = auto-detect
WHISPER_TASK = os.getenv("WHISPER_TASK", "transcribe")  # or "translate"

# --- Make UPLOAD_DIR absolute (anchor to repo root) ---
# Repo root = parent of 'module9_interview_ai' (this file lives in that folder)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# If UPLOAD_DIR is relative, anchor it to the repo root.
# Also handle the old default that started with 'aurorapress/' to avoid doubling.
if not os.path.isabs(UPLOAD_DIR):
    rel = UPLOAD_DIR.replace("\\", "/")
    if rel.startswith("aurorapress/"):
        rel = rel.split("/", 1)[1]  # drop leading 'aurorapress/'
    UPLOAD_DIR = str((PROJECT_ROOT / rel).resolve()) 
os.makedirs(UPLOAD_DIR, exist_ok=True)
