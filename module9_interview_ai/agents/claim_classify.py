# module9_interview_ai/agents/claim_classify.py
from __future__ import annotations
from typing import List, Dict, Optional
from .claim_classifier import ClaimClassifier  # loads your saved model

# -------- Lazy singleton --------
_clf = None

def get_clf() -> ClaimClassifier:
    global _clf
    if _clf is None:
        _clf = ClaimClassifier()   # <-- model loads here, on first use, not at import
    return _clf

def classify_segments_texts(texts: List[str], threshold: Optional[float] = None) -> List[Dict]:
    clf = get_clf()
    return clf.predict(texts, threshold=threshold if threshold is not None else 0.50)

# ------------------------ BaseAgent (uses the same lazy loader) ------------------------
try:
    from ..orchestrator.base import BaseAgent, register
    from ..db import transcripts, analysis
    LEGACY = True
except Exception:
    LEGACY = False

if LEGACY:
    @register
    class ClaimClassifierAgent(BaseAgent):
        name = "ClaimClassifierAgent"
        def run(self, pipeline, tools):
            iid = pipeline.get("interview_id")
            tdoc = transcripts.find_one({"interview_id": iid}) or {}
            segs = tdoc.get("segments", [])
            if not segs:
                return {"claims_predicted": 0, "note": "no segments found"}

            texts = [s["text"] for s in segs]
            preds = get_clf().predict(texts, threshold=0.50)

            total_claims = 0
            for s, p in zip(segs, preds):
                is_claim = 1 if p["label"] == "claim" else 0
                s["claim"] = is_claim
                s["claim_conf"] = float(p["proba_claim"])
                total_claims += is_claim

            transcripts.update_one({"interview_id": iid}, {"$set": {"segments": segs}}, upsert=True)
            analysis.update_one(
                {"interview_id": iid},
                {"$set": {"claim_threshold": 0.50, "claim_total": int(total_claims)}},
                upsert=True
            )
            return {"claims_predicted": int(total_claims), "threshold": 0.50}
