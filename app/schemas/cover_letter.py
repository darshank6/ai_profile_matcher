from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class CoverLetterGenerateRequest(BaseModel):
    resume_id: int = Field(..., gt=0)
    job_id: int = Field(..., gt=0)
    provider: Optional[str] = 'openai'
    model_name: Optional[str] = 'kgpt-reasoning-text'


class CoverLetterResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    cover_letter: str
    provider: str
    model_name: str
    created_at: datetime

    class Config:
        from_attributes = True