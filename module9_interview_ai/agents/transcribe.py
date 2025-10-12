# module9_interview_ai/agents/transcribe.py
from __future__ import annotations
import os, wave, subprocess, json
from typing import List, Dict

from ..orchestrator.base import BaseAgent, register
from ..config import VOSK_MODEL_DIR
from ..db import interviews, transcripts

# Optional deps for diarization
try:
    from pydub import AudioSegment, silence
except Exception:
    AudioSegment = None
    silence = None


# -----------------------------
# 1) ASR: VOSK (yours, unchanged)
# -----------------------------
def transcribe_vosk(audio_path: str, model_dir: str) -> List[dict]:
    from vosk import Model, KaldiRecognizer
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels()!=1 or wf.getsampwidth()!=2 or wf.getframerate() not in (8000,16000,32000,44100,48000):
        wf.close()
        tmp = audio_path + ".mono16k.wav"
        subprocess.check_call(
            ["ffmpeg","-y","-i",audio_path,"-ac","1","-ar","16000",tmp],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        wf = wave.open(tmp, "rb")
    model = Model(model_dir)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    # Clean Fact0 artifacts from transcript text
    def clean_transcript_text(text):
        import re
        text = re.sub(r'\bFact\d+\b', '', text)
        text = re.sub(r'\b(uh|um|you know|like)\b', '', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    segments=[]; start_t=0.0
    while True:
        data = wf.readframes(4000)
        if len(data)==0: break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text = clean_transcript_text(res.get("text",""))
            if text:
                end_t = wf.tell()/float(wf.getframerate())
                segments.append({"start": start_t, "end": end_t, "speaker":"A", "text": text})
                start_t = end_t
    final = json.loads(rec.FinalResult())
    text = clean_transcript_text(final.get("text",""))
    if text:
        end_t = wf.tell()/float(wf.getframerate())
        segments.append({"start": start_t, "end": end_t, "speaker":"A", "text": text})
    wf.close()
    return segments


# -----------------------------
# 2) ASR: Whisper (yours, unchanged)
# -----------------------------
def transcribe_whisper(audio_path: str, model_name: str = "tiny") -> List[dict]:
    """
    CPU-friendly Whisper transcription with memory management.
    Uses the 'tiny' model by default (fast on CPU) and disables fp16.
    """
    import whisper
    import gc
    
    print(f"[Transcription] Loading Whisper model '{model_name}'...")
    
    try:
        # Force garbage collection before loading model
        gc.collect()
        
        # Use tiny model for memory efficiency
        if model_name not in ["tiny", "base"]:
            print(f"[Transcription] Warning: Using '{model_name}' may cause memory issues. Consider using 'tiny' or 'base'.")
            model_name = "tiny"
            
        model = whisper.load_model(model_name, device="cpu")  # force CPU
        print(f"[Transcription] Model loaded successfully.")

        # Quieter + faster settings for CPU with memory optimization
        result = model.transcribe(
            audio_path,
            fp16=False,                         # important for CPU
            temperature=0,
            verbose=False,
            condition_on_previous_text=False,   # reduces drift/speedups for long audio
            no_speech_threshold=0.6,           # reduce memory usage
            logprob_threshold=-1.0,            # reduce memory usage
            compression_ratio_threshold=2.4    # reduce memory usage
        )
        
        # Clean up model from memory
        del model
        gc.collect()
        
    except Exception as e:
        print(f"[Transcription] Whisper error: {e}")
        # Try with even smaller model if available
        if model_name != "tiny":
            print("[Transcription] Retrying with 'tiny' model...")
            return transcribe_whisper(audio_path, "tiny")
        else:
            raise e

    # Clean Fact0 artifacts from transcript text
    def clean_transcript_text(text):
        import re
        text = re.sub(r'\bFact\d+\b', '', text)
        text = re.sub(r'\b(uh|um|you know|like)\b', '', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    return [{
        "start": float(s.get("start", 0.0)),
        "end":   float(s.get("end", 0.0)),
        "speaker": "A",  # diarization will overwrite
        "text": clean_transcript_text(s.get("text") or ""),
    } for s in result.get("segments", [])]


# -----------------------------------------
# 3) Fallback diarization (improved)
# -----------------------------------------
def diarize_fallback(audio_path: str) -> List[Dict]:
    """
    Silence-based segmentation + simple speaker rotation with smoothing.
    Not real diarization, but much nicer than fixed-size chunks.
    Returns: [{start,end,speaker}]
    """
    if AudioSegment is None or silence is None:
        # Minimal last-resort: ~2s blocks
        return _naive_chunks(audio_path)

    audio = AudioSegment.from_file(audio_path)
    # Detect non-silent spans (respect pauses)
    # tweak these two to taste:
    min_silence_len = 350  # ms pause considered a boundary
    silence_thresh  = audio.dBFS - 16  # energy threshold for silence
    nonsilent = silence.detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    # If detection failed, fall back to naive chunks
    if not nonsilent:
        return _naive_chunks(audio_path)

    # Convert to seconds and smooth short gaps (merge segments close to each other)
    merged = []
    gap_merge_ms = 250
    for start_ms, end_ms in nonsilent:
        if not merged:
            merged.append([start_ms, end_ms])
        else:
            prev_s, prev_e = merged[-1]
            if start_ms - prev_e <= gap_merge_ms:
                merged[-1][1] = max(prev_e, end_ms)
            else:
                merged.append([start_ms, end_ms])

    # Map merged spans to rotating speakers
    speakers = ["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"]
    out = []
    for i, (s_ms, e_ms) in enumerate(merged):
        if e_ms - s_ms < 600:  # drop ultra-short blips
            continue
        out.append({
            "start": s_ms / 1000.0,
            "end":   e_ms / 1000.0,
            "speaker": speakers[i % len(speakers)]
        })
    if not out:
        return _naive_chunks(audio_path)
    return out


def _naive_chunks(audio_path: str) -> List[Dict]:
    # If we can probe duration, chunk ~2s; else assume 60s
    try:
        meta = json.loads(subprocess.check_output(
            ["ffprobe","-v","quiet","-print_format","json","-show_format",audio_path]
        ).decode("utf-8"))
        dur = float(meta["format"]["duration"])
    except Exception:
        dur = 60.0
    speakers = ["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"]
    out = []
    t = 0.0; i = 0
    while t < dur:
        t2 = min(dur, t + 2.0)
        out.append({"start": t, "end": t2, "speaker": speakers[i % len(speakers)]})
        t = t2; i += 1
    return out


def assign_speakers(transcript_segments: List[Dict], diar_segments: List[Dict]) -> List[Dict]:
    """Assign each ASR segment the diarized speaker with maximum overlap."""
    if not diar_segments:
        return transcript_segments
    for seg in transcript_segments:
        s0, s1 = float(seg["start"]), float(seg["end"])
        best = (seg.get("speaker","SPEAKER_00"), 0.0)
        for d in diar_segments:
            d0, d1 = float(d["start"]), float(d["end"])
            ov = max(0.0, min(s1, d1) - max(s0, d0))
            if ov > best[1]:
                best = (d["speaker"], ov)
        seg["speaker"] = best[0]
    return transcript_segments


# -----------------------------------------
# 4) Public entrypoint used by orchestrator
# -----------------------------------------
def transcribe_with_diarization(audio_path: str, whisper_model: str = "tiny") -> List[Dict]:
    # 1) ASR
    segments = []
    
    # Try VOSK first if available
    if VOSK_MODEL_DIR and os.path.isdir(VOSK_MODEL_DIR):
        try:
            print("[Transcription] Using Vosk (CPU-friendly).")
            segments = transcribe_vosk(audio_path, VOSK_MODEL_DIR)
        except Exception as e:
            print(f"[Transcription] Vosk failed: {e}")
            segments = []
    
    # If VOSK failed or not available, try Whisper
    if not segments:
        try:
            print(f"[Transcription] Using Whisper '{whisper_model}' (CPU).")
            segments = transcribe_whisper(audio_path, whisper_model)
        except Exception as e:
            print(f"[Transcription] Whisper failed: {e}")
            # Try with tiny model as last resort
            if whisper_model != "tiny":
                try:
                    print("[Transcription] Retrying with tiny model...")
                    segments = transcribe_whisper(audio_path, "tiny")
                except Exception as e2:
                    print(f"[Transcription] Tiny model also failed: {e2}")
                    segments = []
            else:
                segments = []

    if not segments:
        print("[Transcription] All ASR methods failed. Creating fallback segments...")
        # Create a minimal fallback segment
        segments = [{
            "start": 0.0,
            "end": 10.0,
            "speaker": "SPEAKER_00",
            "text": "Transcription failed. Please try with a different audio file or check the audio quality.",
            "claim": 0,
            "claim_conf": 0.0
        }]

    # 2) Fallback diarization
    diar = diarize_fallback(audio_path)

    # 3) Assign speakers by overlap
    segments = assign_speakers(segments, diar)

    # 4) Ensure downstream keys exist
    for s in segments:
        s.setdefault("claim", 0)
        s.setdefault("claim_conf", 0.0)

    return segments


# -----------------------------------------
# 5) Agent wrapper (yours, kept)
# -----------------------------------------
@register
class TranscriptionAgent(BaseAgent):
    name = "TranscriptionAgent"

    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        doc = interviews.find_one({"_id": iid})
        if not doc: raise RuntimeError("Interview not found.")
        audio_path = doc["file_path"]

        segments = transcribe_with_diarization(audio_path, whisper_model="base")
        transcripts.update_one({"interview_id": iid},
            {"$set": {"segments": segments, "stats": {"wpm": 130}}}, upsert=True)
        return {"segments_count": len(segments), "diarization": "fallback"}
