from ..orchestrator.base import BaseAgent, register
from ..db import analysis, quotes, summaries, handoff


@register
class HandoffAgent(BaseAgent):
    name = "HandoffAgent"
    
    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        claims = (analysis.find_one({"interview_id": iid}) or {}).get("claims",[])
        qdoc   = quotes.find_one({"interview_id": iid}) or {}
        sdoc   = summaries.find_one({"interview_id": iid}) or {}
        payload_m6 = {"interview_id": iid, "claims": claims}
        payload_m3 = {"interview_id": iid, "summary": sdoc.get("abstract",""),
                      "angles": sdoc.get("angles",[]), "quotes": qdoc.get("items",[])}

        handoff.update_one({"interview_id": iid},
            {"$set": {"module6": payload_m6, "module3": payload_m3}}, upsert=True)
        # (Optionally POST to your real Module 6 / Module 3 here)
        return {"m6_claims": len(claims), "m3_quotes": len(payload_m3["quotes"])}
