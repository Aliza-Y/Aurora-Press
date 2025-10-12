import os
import sys 

from module9_interview_ai.orchestrator.run_agentic import run_interview_agentic

# ---- MODE A: re-run with existing interview_id (SKIPS ingestion) ----
# INTERVIEW_ID = "fcff3dd6-29ec-43a3-8bc9-f8821211a6b2"  # <- put yours here
# out = run_interview_agentic(interview_id=INTERVIEW_ID)
# print("\n[runner] FINAL (re-run with interview_id):", out)

#---- MODE B: fresh run with a new file (ENABLE this instead if you want new ingestion) ----

AUDIO = r"D:\Final Year Project\aurorapress\sample.m4a"
if not os.path.isfile(AUDIO):
   print(f"[error] File not found: {AUDIO}")
   sys.exit(1)
out = run_interview_agentic(temp_file_path=AUDIO)
print("\n[runner] FINAL (fresh ingestion):", out)