import os, wave, subprocess, json
from typing import List
from ..orchestrator.base import BaseAgent, register
from ..config import VOSK_MODEL_DIR
from ..db import interviews, transcripts

def transcribe_vosk(audio_path: str, model_dir: str) -> List[dict]:
    from vosk import Model, KaldiRecognizer
    wf = wave.open(audio_path, "rb")
    # normalize if needed
    if wf.getnchannels()!=1 or wf.getsampwidth()!=2 or wf.getframerate() not in (8000,16000,32000,44100,48000):
        wf.close()
        tmp = audio_path + ".mono16k.wav"
        subprocess.check_call(["ffmpeg","-y","-i",audio_path,"-ac","1","-ar","16000",tmp],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wf = wave.open(tmp, "rb")
    model = Model(model_dir)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    segments=[]; start_t=0.0
    while True:
        data = wf.readframes(4000)
        if len(data)==0: break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text = res.get("text","").strip()
            if text:
                end_t = wf.tell()/float(wf.getframerate())
                segments.append({"start": start_t, "end": end_t, "speaker":"A", "text": text})
                start_t = end_t
    final = json.loads(rec.FinalResult())
    text = final.get("text","").strip()
    if text:
        end_t = wf.tell()/float(wf.getframerate())
        segments.append({"start": start_t, "end": end_t, "speaker":"A", "text": text})
    wf.close()
    return segments


def transcribe_whisper(audio_path: str, model_name="base") -> List[dict]:
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return [{"start": s["start"], "end": s["end"], "speaker":"A", "text": s["text"].strip()}
            for s in result.get("segments",[])]


@register
class TranscriptionAgent(BaseAgent):
    name = "TranscriptionAgent"
    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        doc = interviews.find_one({"_id": iid})
        if not doc: raise RuntimeError("Interview not found.")
        audio_path = doc["file_path"]
        try:
            if VOSK_MODEL_DIR and os.path.isdir(VOSK_MODEL_DIR):
                segments = transcribe_vosk(audio_path, VOSK_MODEL_DIR)
            else:
                segments = transcribe_whisper(audio_path, "base")
        except Exception:
            segments = transcribe_whisper(audio_path, "base")
        if not segments: raise RuntimeError("ASR produced no segments.")
        transcripts.update_one({"interview_id": iid},
            {"$set": {"segments": segments, "stats": {"wpm": 130}}}, upsert=True)
        return {"segments_count": len(segments)}
