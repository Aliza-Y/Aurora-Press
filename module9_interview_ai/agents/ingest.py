import os, uuid, shutil, subprocess, json
from datetime import datetime
from ..orchestrator.base import BaseAgent, register
from ..config import UPLOAD_DIR
from ..db import interviews


def ffprobe_duration(path: str):
    try:
        out = subprocess.check_output(
            ["ffprobe","-v","error","-show_entries","format=duration","-of","json", path]
        )
        return float(json.loads(out.decode())["format"]["duration"])
    except Exception:
        return None


@register
class IngestionAgent(BaseAgent):
    name = "IngestionAgent"
    
    def run(self, pipeline, tools):
        temp_file_path = pipeline.get("temp_file_path")
        if not temp_file_path or not os.path.exists(temp_file_path):
            iid = pipeline.get("interview_id")
            doc = interviews.find_one({"_id": iid})
            if doc and os.path.exists(doc.get("file_path","")):
                return {"note":"already ingested"}
            raise RuntimeError("No uploaded file found.")
        iid = pipeline.get("interview_id") or str(uuid.uuid4())
        ext = os.path.splitext(temp_file_path)[1] or ".wav"
        dst = os.path.join(UPLOAD_DIR, f"{iid}{ext}")
        shutil.copy2(temp_file_path, dst)
        duration = ffprobe_duration(dst)
        interviews.update_one(
            {"_id": iid},
            {"$set": {"file_path": dst, "title": os.path.basename(dst),
                      "duration": duration, "created_at": datetime.utcnow()}},
            upsert=True
        )
        pipeline["interview_id"] = iid
        return {"interview_id": iid, "file_path": dst, "duration": duration}
