import whisper
import subprocess
import os

AUDIO_IN = "sample.m4a"   # put a short test clip in the same folder

# (Optional) Normalize to 16k mono if your file is odd; whisper can read most formats:
# subprocess.check_call(["ffmpeg", "-y", "-i", AUDIO_IN, "-ac", "1", "-ar", "16000", "sample_16k.wav"])
# AUDIO_IN = "sample_16k.wav"

print("Loading model (base) on CPU...")
model = whisper.load_model("base")  # first run auto-downloads the model

print("Transcribing...")
# Force CPU explicitly (good for i3 laptops)
result = model.transcribe(AUDIO_IN, task="transcribe", language=None, verbose=False)
print("=== TRANSCRIPT ===")
print(result.get("text", "").strip())
