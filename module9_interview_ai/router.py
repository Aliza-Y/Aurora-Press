import os, tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from .models import UploadResp, PipelineStatus
from .orchestrator.orchestrator import run_pipeline
from .orchestrator.base import REGISTRY
from .db import pipelines, transcripts, analysis, quotes, summaries, sources, relationships, handoff, interviews

# ensure agents are registered
from .agents import *  # noqa: F401,F403

router = APIRouter(prefix="/m9", tags=["module9"])


@router.post("/upload", response_model=UploadResp)
async def upload(file: UploadFile = File(...), title: str = Form(None)):
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    # create pipeline doc
    import uuid
    iid = str(uuid.uuid4())
    pipelines.update_one(
        {"interview_id": iid},
        {"$set": {
            "interview_id": iid, 
            "status":"running", 
            "steps":{}, 
            "errors":[], 
            "temp_file_path": temp_path,
            "title": title or os.path.splitext(file.filename)[0]  # Use provided title or filename without extension
        }},
        upsert=True
    )
    return {"interview_id": iid, "temp_file_path": temp_path}


@router.post("/pipeline/tick", response_model=PipelineStatus)
def tick(interview_id: str = Query(...)):
    # Get the pipeline document to find the temp file path
    p = pipelines.find_one({"interview_id": interview_id})
    if not p:
        raise HTTPException(404, "Pipeline not found")
    
    temp_file_path = p.get("temp_file_path")
    if not temp_file_path or not os.path.exists(temp_file_path):
        raise HTTPException(400, "Audio file not found")
    
    try:
        print(f"[Router] Starting pipeline for interview {interview_id}")
        
        # Run the full pipeline
        title = p.get("title")
        result = run_pipeline(temp_file_path, title=title, interview_id=interview_id)
        
        # Update the result with the correct interview_id
        result["interview_id"] = interview_id
        
        # Update pipeline status to completed
        pipelines.update_one(
            {"interview_id": interview_id},
            {"$set": {"status": "completed", "result": result}}
        )
        
        print(f"[Router] Pipeline completed successfully for interview {interview_id}")
        return PipelineStatus(interview_id=interview_id, status="completed",
                              steps={"transcription": "completed", "analysis": "completed", "quotes": "completed", "summary": "completed"}, 
                              errors=[])
                              
    except Exception as e:
        print(f"[Router] Pipeline failed for interview {interview_id}: {e}")
        import traceback
        print(f"[Router] Full traceback: {traceback.format_exc()}")
        
        # Update pipeline status to error
        error_obj = {"message": str(e), "type": type(e).__name__}
        pipelines.update_one(
            {"interview_id": interview_id},
            {"$set": {"status": "error", "errors": [error_obj]}}
        )
        return PipelineStatus(interview_id=interview_id, status="error",
                              steps={}, errors=[error_obj])


@router.get("/pipeline/status", response_model=PipelineStatus)
def status(interview_id: str):
    p = pipelines.find_one({"interview_id": interview_id})
    if not p:
        raise HTTPException(404, "Pipeline not found")
    
    # Ensure errors are properly formatted as list of dictionaries
    errors = p.get("errors", [])
    if errors and isinstance(errors[0], str):
        # Convert string errors to proper error objects
        errors = [{"message": error, "type": "UnknownError"} for error in errors]
    
    return PipelineStatus(interview_id=interview_id, status=p.get("status","running"),
                          steps=p.get("steps",{}), errors=errors)


@router.get("/transcript")
def get_transcript(interview_id: str):
    doc = transcripts.find_one({"interview_id": interview_id}, {"_id":0})
    if not doc: raise HTTPException(404, "Transcript not found")
    return doc


@router.get("/analysis")
def get_analysis(interview_id: str):
    doc = analysis.find_one({"interview_id": interview_id}, {"_id":0})
    if not doc: raise HTTPException(404, "Analysis not found")
    return doc


@router.get("/quotes")
def get_quotes(interview_id: str):
    doc = quotes.find_one({"interview_id": interview_id}, {"_id":0})
    if not doc: raise HTTPException(404, "Quotes not found")
    return doc


@router.get("/summary")
def get_summary(interview_id: str):
    doc = summaries.find_one({"interview_id": interview_id}, {"_id":0})
    if not doc: raise HTTPException(404, "Summary not found")
    return doc


@router.get("/sources")
def get_sources(interview_id: str):
    srcs = list(sources.find({}, {"_id":0}))
    rels = list(relationships.find({}, {"_id":0}))
    return {"sources": srcs, "relationships": rels}


@router.get("/handoff")
def get_handoff(interview_id: str):
    doc = handoff.find_one({"interview_id": interview_id}, {"_id":0})
    if not doc: raise HTTPException(404, "No handoff payloads")
    return doc


@router.get("/interviews")
def list_interviews():
    """Get list of all interviews for the journalist"""
    interview_list = list(interviews.find({}, {"_id": 0}).sort("created_at", -1))
    return {"interviews": interview_list}


@router.delete("/interviews/{interview_id}")
def delete_interview(interview_id: str):
    """Delete an interview and all its associated data"""
    # Delete from all collections
    interviews.delete_many({"interview_id": interview_id})
    transcripts.delete_many({"interview_id": interview_id})
    quotes.delete_many({"interview_id": interview_id})
    summaries.delete_many({"interview_id": interview_id})
    analysis.delete_many({"interview_id": interview_id})
    pipelines.delete_many({"interview_id": interview_id})
    
    return {"message": "Interview deleted successfully"}


@router.get("/debug/agents")
def debug_agents():
    return {"registered": sorted(list(REGISTRY.keys()))}
