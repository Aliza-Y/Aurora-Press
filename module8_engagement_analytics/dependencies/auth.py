from fastapi import Header, HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env at startup

API_KEY = os.getenv("API_KEY")  # expect supersecret123


def require_api_key(x_api_key: str = Header(..., description="AuroraPress Module 8 API Key")):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
