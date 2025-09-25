from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, summaries


@register
class SummaryAnglesAgent(BaseAgent):
    name = "SummaryAnglesAgent"
    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        tdoc = transcripts.find_one({"interview_id": iid})
        if not tdoc: raise RuntimeError("Transcript missing.")
        text = " ".join(s["text"] for s in tdoc["segments"]).strip()
        if not text: raise RuntimeError("Transcript empty.")

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summ = TextRankSummarizer()
        sents = [str(s) for s in summ(parser.document, 4)]
        abstract = " ".join(sents)
        angles = ["Policy impact", "Human-interest angle", "Data/evidence angle"]

        summaries.update_one({"interview_id": iid},
            {"$set": {"abstract": abstract, "angles": angles}}, upsert=True)
        return {"summary_len": len(abstract), "angles": len(angles)}
