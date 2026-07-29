from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: str
    file_size: int
    extracted_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True