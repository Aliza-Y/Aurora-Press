# module9_interview_ai/orchestrator/orchestrator.py
# module9_interview_ai/orchestrator/orchestrator.py

from module9_interview_ai.agents.transcribe import transcribe_with_diarization
from module9_interview_ai.agents.claim_classify import classify_segments_texts
from module9_interview_ai.agents.quote_miner import mine_quotes
from module9_interview_ai.agents.summary_angles import summarize_and_angles
from module9_interview_ai.db import save_interview


def apply_claims(transcript_segments, threshold=None):
    try:
        preds = classify_segments_texts([seg["text"] for seg in transcript_segments], threshold=threshold)
        for seg, p in zip(transcript_segments, preds):
            # Handle different prediction formats
            if isinstance(p, dict):
                # Check for both old and new format
                if "label" in p and "proba_claim" in p:
                    # New format from claim_classify.py
                    seg["claim"] = 1 if p["label"] == "claim" else 0
                    seg["claim_conf"] = float(p["proba_claim"])
                elif "is_claim" in p and "confidence" in p:
                    # Old format
                    seg["claim"] = 1 if p.get("is_claim", False) else 0
                    seg["claim_conf"] = float(p.get("confidence", 0.0))
                else:
                    # Fallback
                    seg["claim"] = 0
                    seg["claim_conf"] = 0.0
            else:
                # Fallback if prediction format is unexpected
                seg["claim"] = 0
                seg["claim_conf"] = 0.0
    except Exception as e:
        # If claim classification fails, set default values
        print(f"Warning: Claim classification failed: {e}")
        for seg in transcript_segments:
            seg["claim"] = 0
            seg["claim_conf"] = 0.0
    return transcript_segments


def run_pipeline(audio_path: str, title: str = None, interview_id: str = None) -> dict:
    try:
        print(f"[Pipeline] Starting transcription for interview {interview_id}")
        segments = transcribe_with_diarization(audio_path)        # + speakers (fallback)
        print(f"[Pipeline] Transcription completed: {len(segments)} segments")
        
        print(f"[Pipeline] Applying claim classification...")
        segments = apply_claims(segments)                         # + claim labels
        claim_count = sum(1 for s in segments if s.get("claim", 0) == 1)
        print(f"[Pipeline] Claims classified: {claim_count} claims found")
        
        print(f"[Pipeline] Mining quotes...")
        quotes = mine_quotes(segments, min_conf=0.60)             # quotes from confident claims
        print(f"[Pipeline] Quotes extracted: {len(quotes)} quotes")
        
        print(f"[Pipeline] Generating summary...")
        sa = summarize_and_angles(segments)                       # summary + angles (stub or LLM)
        print(f"[Pipeline] Summary generated: {len(sa.get('summary', ''))} characters")
        
        payload = {
            "title": title,
            "segments": segments,
            "quotes": quotes,
            "summary": sa.get("summary"),
            "angles": sa.get("angles", []),
        }
        
        print(f"[Pipeline] Saving to database...")
        saved_interview_id = save_interview(payload, interview_id)
        payload["interview_id"] = saved_interview_id
        print(f"[Pipeline] Pipeline completed successfully for interview {saved_interview_id}")
        return payload
        
    except Exception as e:
        print(f"[Pipeline] Error in run_pipeline: {e}")
        import traceback
        print(f"[Pipeline] Full traceback: {traceback.format_exc()}")
        raise e
