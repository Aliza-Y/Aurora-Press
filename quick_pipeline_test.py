from module9_interview_ai.orchestrator.orchestrator import run_pipeline

AUDIO = r"D:\Final Year Project\aurorapress\sample.m4a"
out = run_pipeline(AUDIO, title="Test Interview")

print(out.keys(), len(out["segments"]), len(out["quotes"]))
print(out["segments"][0])
