import re

# Optional imports for NLP analysis
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAVE_SPACY = True
except (ImportError, OSError):
    nlp = None
    HAVE_SPACY = False
    print("Warning: spacy or en_core_web_sm model not available. NLP analysis will be disabled.")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAVE_VADER = True
except ImportError:
    HAVE_VADER = False
    # Silent warning - vaderSentiment is optional

from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, analysis

sid = SentimentIntensityAnalyzer() if HAVE_VADER else None
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
            
            # Only do NLP analysis if spacy is available
            if nlp is not None:
                doc = nlp(txt)
                ents += [{"segment_idx": i, "text": e.text, "label": e.label_} for e in doc.ents]
            else:
                ents += []
            
            # Only do sentiment analysis if vaderSentiment is available
            if sid is not None:
                comp = sid.polarity_scores(txt)["compound"]
                sents.append({"segment_idx": i, "compound": comp})
            else:
                sents.append({"segment_idx": i, "compound": 0.0})
                
            if CLAIM_RE.search(txt):
                claims.append({"segment_idx": i, "text": txt})

        analysis.update_one({"interview_id": iid},
            {"$set": {"entities": ents, "sentiments": sents, "claims": claims}}, upsert=True)
        return {"entities": len(ents), "claims": len(claims)}
