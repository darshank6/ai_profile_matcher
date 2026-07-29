from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobCreate(BaseModel):

    title: str

    company_name: Optional[str] = None

    description: str

    required_skills: Optional[str] = None


class JobUpdate(BaseModel):

    title: Optional[str] = None

    company_name: Optional[str] = None

    description: Optional[str] = None

    required_skills: Optional[str] = None


class JobResponse(BaseModel):

    id: int

    user_id: int

    title: str

    company_name: Optional[str]

    description: str

    required_skills: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True