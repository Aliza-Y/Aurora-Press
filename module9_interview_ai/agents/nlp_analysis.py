import re
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, analysis

nlp = spacy.load("en_core_web_sm")
sid = SentimentIntensityAnalyzer()
CLAIM_RE = re.compile(r"\b(according to|report(s)?|evidence|data shows|study|percent|%)\b", re.I)


@register
class NlpAnalysisAgent(BaseAgent):
    name = "NlpAnalysisAgent"
    
    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        tdoc = transcripts.find_one({"interview_id": iid})
        if not tdoc: raise RuntimeError("Transcript missing.")
        segs = tdoc["segments"]

        ents=[]; sents=[]; claims=[]
        for i, s in enumerate(segs):
            txt = s["text"]
            doc = nlp(txt)
            ents += [{"segment_idx": i, "text": e.text, "label": e.label_} for e in doc.ents]
            comp = sid.polarity_scores(txt)["compound"]
            sents.append({"segment_idx": i, "compound": comp})
            if CLAIM_RE.search(txt):
                claims.append({"segment_idx": i, "text": txt})

        analysis.update_one({"interview_id": iid},
            {"$set": {"entities": ents, "sentiments": sents, "claims": claims}}, upsert=True)
        return {"entities": len(ents), "claims": len(claims)}
