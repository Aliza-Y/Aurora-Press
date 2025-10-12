# importing agents registers them into REGISTRY via @register decorator

def _safe_import(path: str, name: str):
    try:
        module = __import__(path, fromlist=[name])
        return getattr(module, name)
    except Exception:
        # Optionally log the exception if you have a logger
        return None


from .ingest import IngestionAgent                # noqa: F401
from .transcribe import TranscriptionAgent        # noqa: F401
from .nlp_analysis import NlpAnalysisAgent        # noqa: F401
# from .quote_miner import QuoteMinerAgent          # noqa: F401  # Temporarily disabled due to memory issues
from .summary_angles import SummaryAnglesAgent    # noqa: F401
from .source_manager import SourceManagerAgent    # noqa: F401
from .handoff import HandoffAgent                 # noqa: F401


# ClaimClassifierAgent must exist now (we just added it back). This safe import
# avoids crashing the whole package if it’s removed in the future.
_safe_import('module9_interview_ai.agents.claim_classify', 'ClaimClassifierAgent')
