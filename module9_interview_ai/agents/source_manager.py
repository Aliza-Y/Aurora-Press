from ..orchestrator.base import BaseAgent, register
from ..db import analysis, sources, relationships

TRUSTED = {"Reuters","Associated Press","AP","BBC","The Guardian","Al Jazeera","Bloomberg"}


def credibility(org=None, verified=False, flagged=False, has_web=True) -> int:
    score=50
    if org in TRUSTED: score += 20
    if verified: score += 10
    if flagged: score -= 15
    if not has_web: score -= 10
    return max(0, min(100, score))


@register
class SourceManagerAgent(BaseAgent):
    name = "SourceManagerAgent"
    
    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        adoc = analysis.find_one({"interview_id": iid}) or {}
        ents = adoc.get("entities", [])
        names = [e["text"] for e in ents if e["label"] in ("PERSON","ORG")]

        seen=set(); unique=[]
        for n in names:
            if n not in seen:
                unique.append(n); seen.add(n)

        for n in unique:
            sources.update_one({"name": n},
                {"$setOnInsert": {"org": None, "topics": [], "credibility": credibility(None)}},
                upsert=True)

        # simple co-mentions for this interview
        for i in range(len(unique)):
            for j in range(i+1, len(unique)):
                a,b = sorted([unique[i], unique[j]])
                relationships.update_one({"a":a,"b":b}, {"$inc":{"weight":1}}, upsert=True)

        return {"sources": len(unique), "edges_added": max(0, (len(unique)*(len(unique)-1))//2)}
