from pymongo import MongoClient
from .config import MONGO_URI, DB_NAME
import uuid
from datetime import datetime

_client = MongoClient(MONGO_URI)
db = _client[DB_NAME]

interviews = db["m9_interviews"]
transcripts = db["m9_transcripts"]
analysis = db["m9_analysis"]
quotes = db["m9_quotes"]
summaries = db["m9_summaries"]
sources = db["m9_sources"]
relationships = db["m9_relationships"]
pipelines = db["m9_pipelines"]
handoff = db["m9_handoff_bridge"]


def save_interview(payload, interview_id=None):
    """
    Save interview data to the database and return the interview_id.
    
    Args:
        payload (dict): Contains title, segments, quotes, summary, angles
        interview_id (str, optional): Use provided interview_id instead of generating new one
        
    Returns:
        str: The interview_id
    """
    # Use provided interview_id or generate a new one
    if not interview_id:
        interview_id = str(uuid.uuid4())
    
    # Prepare the interview document
    interview_doc = {
        "interview_id": interview_id,
        "title": payload.get("title", "Untitled Interview"),
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    
    # Save to interviews collection
    interviews.insert_one(interview_doc)
    
    # Save transcript if segments exist
    if payload.get("segments"):
        transcript_doc = {
            "interview_id": interview_id,
            "segments": payload["segments"]
        }
        transcripts.insert_one(transcript_doc)
    
    # Save quotes if they exist
    if payload.get("quotes"):
        quotes_doc = {
            "interview_id": interview_id,
            "quotes": payload["quotes"]
        }
        quotes.insert_one(quotes_doc)
    
    # Save summary if it exists
    if payload.get("summary") or payload.get("angles"):
        summary_doc = {
            "interview_id": interview_id,
            "summary": payload.get("summary", ""),
            "angles": payload.get("angles", [])
        }
        summaries.insert_one(summary_doc)
    
    return interview_id
