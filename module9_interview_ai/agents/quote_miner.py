import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, analysis, quotes


def length_penalty(text: str) -> float:
    L = len(text.split())
    return 1.0 if 8 <= L <= 28 else 0.6


@register
class QuoteMinerAgent(BaseAgent):
    name = "QuoteMinerAgent"
    
    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        tdoc = transcripts.find_one({"interview_id": iid})
        adoc = analysis.find_one({"interview_id": iid})
        if not tdoc or not adoc: raise RuntimeError("Transcript/Analysis missing.")
        segs = tdoc["segments"]; texts = [s["text"] for s in segs]
        if not texts: raise RuntimeError("No text to score.")

        tfidf = TfidfVectorizer(min_df=1)
        tf = tfidf.fit_transform(texts).toarray()
        tfscore = tf.sum(axis=1)

        ent_idx = {e["segment_idx"] for e in adoc.get("entities", []) if e["label"] in ("PERSON","ORG")}
        sent_map = {s["segment_idx"]: s["compound"] for s in adoc.get("sentiments", [])}

        scores=[]
        for i, s in enumerate(segs):
            score = 0.5*tfscore[i] + 0.3*(1 if i in ent_idx else 0) + 0.2*abs(sent_map.get(i,0))
            score *= length_penalty(s["text"])
            scores.append(score)

        order = list(np.argsort(scores))[::-1]
        top_idx = order[: min(5, len(order))]
        items=[]
        for i in top_idx:
            ctx_prev = segs[i-1]["text"] if i-1>=0 else ""
            ctx_next = segs[i+1]["text"] if i+1<len(segs) else ""
            items.append({
                "text": segs[i]["text"], "start": segs[i]["start"], "end": segs[i]["end"],
                "score": float(scores[i]), "entities": [], "sentiment": float(sent_map.get(i,0)),
                "context": {"prev": ctx_prev, "next": ctx_next}
            })
        quotes.update_one({"interview_id": iid}, {"$set": {"items": items}}, upsert=True)
        return {"quotes": len(items)}
