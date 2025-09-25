from pymongo import MongoClient
from .config import MONGO_URI, DB_NAME

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
