from __future__ import annotations
import os
from typing import List, Dict, Union

import torch

# Optional imports for transformers
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    HAVE_TRANSFORMERS = True
except ImportError:
    HAVE_TRANSFORMERS = False
    print("Warning: transformers not available. Claim classification will be disabled.")

# Default model dir inside the repo; overridable via CLAIM_MODEL_DIR
_DEFAULT_MODEL_DIR = os.environ.get(
    "CLAIM_MODEL_DIR",
    os.path.join(os.path.dirname(__file__), "..", "models", "claim_classifier_distilbert")
)


class ClaimClassifier:
    def __init__(self, model_dir: str = _DEFAULT_MODEL_DIR, device: Union[str,int,None] = None):
        if not HAVE_TRANSFORMERS:
            self.model = None
            self.tokenizer = None
            self.device = "cpu"
            return
            
        # pick GPU if available, else CPU
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()

        cfg = self.model.config

        # --- Robust label maps ---
        # Try to read label2id directly (labels -> ids)
        label2id = getattr(cfg, "label2id", None)
        id2label = getattr(cfg, "id2label", None)

        if isinstance(label2id, dict) and len(label2id) > 0:
            # Ensure values are ints and keys are strings
            self.label2id = {str(k): int(v) for k, v in label2id.items()}
            # Build id2label from label2id if needed
            self.id2label = {v: k for k, v in self.label2id.items()}
        elif isinstance(id2label, dict) and len(id2label) > 0:
            # HF sometimes stores keys as strings, values as labels
            # Normalize keys to ints
            self.id2label = {int(k): str(v) for k, v in id2label.items()}
            self.label2id = {v: k for k, v in self.id2label.items()}
        else:
            # Safe default
            self.label2id = {"non_claim": 0, "claim": 1}
            self.id2label = {0: "non_claim", 1: "claim"}

        # Sanity: must have the expected labels
        if "claim" not in self.label2id or "non_claim" not in self.label2id:
            # Fall back if the config used different strings
            # Try to infer by sorting labels alphabetically as a last resort
            # (You can customize this mapping if you used different label names.)
            self.label2id = {"non_claim": 0, "claim": 1}
            self.id2label = {0: "non_claim", 1: "claim"}

    @torch.inference_mode()
    def predict(self, texts: List[str], threshold: float = 0.50) -> List[Dict]:
        if not HAVE_TRANSFORMERS or self.model is None:
            # Fallback: return neutral predictions
            return [{
                "label": "non_claim",
                "score": 0.5,
                "proba_claim": 0.5,
                "proba_non_claim": 0.5,
            } for _ in texts]
            
        enc = self.tokenizer(
            texts,
            truncation=True,
            padding=True,     # dynamic per-batch padding
            max_length=512,
            return_tensors="pt",
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}
        logits = self.model(**enc).logits
        probs = torch.softmax(logits, dim=-1)
        proba_claim = probs[:, self.label2id["claim"]]
        proba_non   = probs[:, self.label2id["non_claim"]]
        preds = (proba_claim >= threshold).long()

        out = []
        for i, p in enumerate(preds.tolist()):
            out.append({
                "label": self.id2label[p],
                "score": float(proba_claim[i] if p == 1 else proba_non[i]),
                "proba_claim": float(proba_claim[i]),
                "proba_non_claim": float(proba_non[i]),
            })
        return out


if __name__ == "__main__":
    clf = ClaimClassifier()
    print(clf.predict([
        "The government will cut taxes by 10% next year.",
        "Thanks for joining us today."
    ]))
