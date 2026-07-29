from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AIResumeAnalyzeRequest(BaseModel):
    provider: Optional[str] = 'openai'
    model_name: Optional[str] = 'kgpt-reasoning-text'


class AIResumeReportResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    summary: str
    strengths: str
    weaknesses: str
    suggestions: str
    provider: str
    model_name: str
    created_at: datetime

    class Config:
        from_attributes = True