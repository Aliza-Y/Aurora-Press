import re
from typing import List, Dict
import numpy as np
from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, analysis, quotes

SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')

def _clean_text(t: str) -> str:
    # light cleanup: drop stray artifacts (like ASR “Fact0”), fillers, extra spaces
    t = re.sub(r'\bFact\d+\b', '', t)
    t = re.sub(r'\b(uh|um|you know|like)\b', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def _split_into_sentences(text: str) -> List[str]:
    text = _clean_text(text)
    # fall back if no punctuation
    if not re.search(r'[.!?]', text):
        return [text] if text else []
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]

def _segment_score(seg: Dict) -> float:
    """
    Score prioritizes: high claim_conf, reasonable length (8–28 words), mild sentiment, contains numbers or nouns.
    """
    text = seg.get("text","")
    L = len(text.split())
    len_bonus = 1.0 if 8 <= L <= 28 else 0.7
    conf = float(seg.get("claim_conf", 0.0))
    num_bonus = 1.15 if re.search(r'\d', text) else 1.0
    return conf * len_bonus * num_bonus

def _promote_sentence(sent: str) -> float:
    # sentence-level bump if it looks like a crisp assertion
    bump = 1.0
    if re.search(r'\b(will|is|are|has|have|should|must|plans?|expects?)\b', sent, re.I):
        bump *= 1.15
    if re.search(r'\d', sent):
        bump *= 1.10
    return bump

def mine_quotes(segments: List[Dict], min_conf: float = 0.60, top_k: int = 5) -> List[Dict]:
    """
    Extract quotable lines:
      1) filter segments by claim_conf >= min_conf
      2) split into sentences, score, choose best few
    Returns: [{text, start, end, speaker, confidence, score}]
    """
    candidates = [s for s in segments if float(s.get("claim_conf", 0.0)) >= min_conf and _clean_text(s.get("text",""))]
    if not candidates:
        return []

    scored = []
    for s in candidates:
        start, end, speaker = float(s.get("start",0)), float(s.get("end",0)), s.get("speaker","SPEAKER_00")
        base = _segment_score(s)
        sents = _split_into_sentences(s.get("text",""))
        if not sents:
            scored.append({
                "text": _clean_text(s.get("text","")),
                "start": start, "end": end, "speaker": speaker,
                "confidence": float(s.get("claim_conf",0.0)),
                "score": base
            })
            continue
        # choose top sentence(s) within the segment
        for sent in sents:
            sc = base * _promote_sentence(sent)
            scored.append({
                "text": sent,
                "start": start, "end": end, "speaker": speaker,
                "confidence": float(s.get("claim_conf",0.0)),
                "score": sc
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

@register
class QuoteMinerAgent(BaseAgent):
    name = "QuoteMinerAgent"

    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        tdoc = transcripts.find_one({"interview_id": iid}) or {}
        segs = tdoc.get("segments", [])
        if not segs:
            return {"quotes": 0}

        items = mine_quotes(segs, min_conf=0.60, top_k=5)
        quotes.update_one({"interview_id": iid}, {"$set": {"quotes": items}}, upsert=True)
        return {"quotes": len(items)}
