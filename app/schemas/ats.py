from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ATSRequest(BaseModel):
    resume_id: int
    job_id: int


class ATSResponse(BaseModel):
    report_id: int
    ats_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    recommendations: list[str]


class ATSReportResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    resume_text: Optional[str]
    job_description_text: Optional[str]
    extracted_resume_skills: Optional[str]
    extracted_job_skills: Optional[str]
    matched_skills: Optional[str]
    missing_skills: Optional[str]
    strengths: Optional[str]
    recommendations: Optional[str]
    match_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True