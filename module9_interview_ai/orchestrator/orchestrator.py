import subprocess, json, os
from datetime import datetime
from .base import REGISTRY
from ..db import pipelines
# ✅ force-load all agents so @register runs (critical)
from .. import agents  # noqa: F401

PIPE_STEPS = [
    "IngestionAgent",
    "TranscriptionAgent",
    "NlpAnalysisAgent",
    "QuoteMinerAgent",
    "SummaryAnglesAgent",
    "SourceManagerAgent",
    "ClaimClassifierAgent",
    "HandoffAgent"
]


def get_pipeline(interview_id: str) -> dict:
    p = pipelines.find_one({"interview_id": interview_id})
    return p or {"interview_id": interview_id, "status":"running", "steps":{}, "errors":[]}


def update_pipeline(p: dict):
    pipelines.update_one({"interview_id": p["interview_id"]}, {"$set": p}, upsert=True)


def run_one_tick(interview_id: str, tools: dict) -> dict:
    p = get_pipeline(interview_id)
    for step in PIPE_STEPS:
        st = p["steps"].get(step, {})
        if not st.get("ok"):
            try:
                out = REGISTRY[step].run(p, tools)
                p["steps"][step] = {"ok": True, **out}
            except Exception as e:
                msg = str(e)
                p["errors"].append({"step": step, "message": msg, "ts": datetime.utcnow().isoformat()})
                p["steps"][step] = {"ok": False, "error": msg}
            update_pipeline(p)
            break
    else:
        p["status"] = "done"
        update_pipeline(p)
    return p
