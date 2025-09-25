import os, tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from .models import UploadResp, PipelineStatus
from .orchestrator.orchestrator import run_one_tick, get_pipeline
from .orchestrator.base import REGISTRY
from .db import pipelines, transcripts, analysis, quotes, summaries, sources, relationships, handoff

# ensure agents are registered
from .agents import *  # noqa: F401,F403

router = APIRouter(prefix="/m9", tags=["module9"])


@router.post("/upload", response_model=UploadResp)
async def upload(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    # create pipeline doc
    import uuid
    iid = str(uuid.uuid4())
    pipelines.update_one(
        {"interview_id": iid},
        {"$set": {"interview_id": iid, "status":"running", "steps":{}, "errors":[], "temp_file_path": temp_path}},
        upsert=True
    )
    return {"interview_id": iid, "temp_file_path": temp_path}


@router.post("/pipeline/tick", response_model=PipelineStatus)
def tick(interview_id: str = Query(...)):
    p = run_one_tick(interview_id, tools={})
    return PipelineStatus(interview_id=interview_id, status=p.get("status","running"),
                          steps=p.get("steps",{}), errors=p.get("errors",[]))


@router.get("/pipeline/status", response_model=PipelineStatus)
def status(interview_id: str):
    p = get_pipeline(interview_id)
    return PipelineStatus(interview_id=interview_id, status=p.get("status","running"),
                          steps=p.get("steps",{}), errors=p.get("errors",[]))


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


@router.get("/debug/agents")
def debug_agents():
    return {"registered": sorted(list(REGISTRY.keys()))}
