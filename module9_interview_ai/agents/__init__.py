# importing agents registers them into REGISTRY via @register decorator
from .ingest import IngestionAgent     # noqa: F401
from .transcribe import TranscriptionAgent  # noqa: F401
from .nlp_analysis import NlpAnalysisAgent  # noqa: F401
from .quote_miner import QuoteMinerAgent    # noqa: F401
from .summary_angles import SummaryAnglesAgent  # noqa: F401
from .source_manager import SourceManagerAgent  # noqa: F401
from .handoff import HandoffAgent          # noqa: F401
from .claim_classify import ClaimClassifierAgent  # noqa: F401


