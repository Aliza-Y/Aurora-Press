from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, analysis
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "claim_distilbert"

_tok = None
_model = None


def _load_model():
    global _tok, _model
    if _tok is None or _model is None:
        print(f"[ClaimClassifierAgent] loading {MODEL_DIR}")
        _tok = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        _model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
        _model.eval()
    return _tok, _model


def score_claim(text: str, max_len=192) -> float:
    tok, model = _load_model()
    with torch.no_grad():
        x = tok(text, return_tensors="pt", truncation=True, max_length=max_len)
        logits = model(**x).logits
        prob = torch.softmax(logits, dim=-1)[0,1].item()
        return float(prob)


@register
class ClaimClassifierAgent(BaseAgent):
    name = "ClaimClassifierAgent"

    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        tx = transcripts.find_one({"interview_id": iid}) or {}
        segs = tx.get("segments", [])
        if not segs:
            return {"claims_predicted": 0}

        results = []
        for i, s in enumerate(segs):
            p = score_claim(s["text"])
            if p >= 0.55:  # threshold; tune 0.5-0.65 after a few runs
                results.append({"seg_idx": i, "text": s["text"], "score": round(p, 3)})

        analysis.update_one({"interview_id": iid},
                            {"$set": {"claim_candidates": results}},
                            upsert=True)
        return {"claims_predicted": len(results), "threshold": 0.55}
