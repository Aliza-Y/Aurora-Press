from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, os
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "claim_distilbert"

tok = AutoTokenizer.from_pretrained(str(MODEL_DIR))
model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))


def score(text: str) -> float:
    with torch.no_grad():
        x = tok(text, return_tensors="pt", truncation=True, max_length=192)
        logits = model(**x).logits
        prob = torch.softmax(logits, dim=-1)[0,1].item()
        return prob


samples = [
    "Last year, he got 15 billion views across social media platforms.",
    "I think it was a great event.",
    "UVU hosted 3,000 students this month according to organizers."
]
for s in samples:
    print(round(score(s), 3), s)
