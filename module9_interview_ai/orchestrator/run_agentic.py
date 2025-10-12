# module9_interview_ai/orchestrator/run_agentic.py
from __future__ import annotations
from typing import List, Dict, Any

# IMPORTANT: importing agents registers them into REGISTRY via @register
from module9_interview_ai import agents as _load_agents  # <-- ensures REGISTRY is filled
from .base import REGISTRY


def run_agents_in_order(order: List[str], pipeline: Dict[str, Any]) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    print("[runner] starting agentic pipeline...")
    for name in order:
        agent = REGISTRY.get(name)  # REGISTRY stores instances
        if not agent:
            raise RuntimeError(f"Agent not found in REGISTRY: {name}")
        print(f"[runner] → {name} running...")
        out = agent.run(pipeline, tools=None)
        results[name] = out
        print(f"[runner] ← {name} done. Output: {out}")
    print("[runner] pipeline completed.")
    return results


def run_interview_agentic(temp_file_path: str | None = None, interview_id: str | None = None) -> Dict[str, Any]:
    """
    Either pass a temp_file_path (new upload), or an existing interview_id stored in DB.
    """
    pipeline: Dict[str, Any] = {}
    if temp_file_path:
        pipeline["temp_file_path"] = temp_file_path
    if interview_id:
        pipeline["interview_id"] = interview_id

    order = [
        "IngestionAgent",
        "TranscriptionAgent",
        "ClaimClassifierAgent",
        "NlpAnalysisAgent",   # optional
        "QuoteMinerAgent",
        "SummaryAnglesAgent",
        "HandoffAgent",
    ]
    return run_agents_in_order(order, pipeline)

if __name__ == "__main__":
    # Handy direct run:
    AUDIO = r"D:\Final Year Project\aurorapress\module9_interview_ai\sample.m4a"  # <- change path if needed
    out = run_interview_agentic(temp_file_path=AUDIO)
    print("\n[runner] FINAL:", out)
