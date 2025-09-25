import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "aurorapress")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "aurorapress/module9_interview_ai/uploads")
VOSK_MODEL_DIR = os.getenv("VOSK_MODEL_DIR", "")

# Whisper settings (force Whisper by leaving VOSK empty)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "")   # empty = auto-detect
WHISPER_TASK = os.getenv("WHISPER_TASK", "transcribe")  # or "translate"

os.makedirs(UPLOAD_DIR, exist_ok=True)
