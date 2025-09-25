from pydantic import BaseModel
from typing import Dict, Any, List


class UploadResp(BaseModel):
    interview_id: str
    temp_file_path: str


class PipelineStatus(BaseModel):
    interview_id: str
    status: str
    steps: Dict[str, Any]
    errors: List[Dict[str, Any]] = []
