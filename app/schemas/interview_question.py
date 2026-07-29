from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class InterviewQuestionGenerateRequest(BaseModel):
    resume_id: int = Field(..., gt=0, examples=[2])
    job_id: int = Field(..., gt=0, examples=[1])
    provider: Optional[str] = 'openai'
    model_name: Optional[str] = 'kgpt-reasoning-text'

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        allowed = {"ollama", "openai"}

        if value.lower() not in allowed:
            raise ValueError("provider must be either 'ollama' or 'openai'")

        return value.lower()


class InterviewQuestionUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("title cannot be empty")

        return value


class InterviewQuestionBatchDeleteRequest(BaseModel):
    report_ids: List[int] = Field(..., min_length=1)

    @field_validator("report_ids")
    @classmethod
    def validate_report_ids(cls, values: List[int]) -> List[int]:
        if any(report_id <= 0 for report_id in values):
            raise ValueError("all report ids must be positive integers")

        return values


class InterviewQuestionReportResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    title: str
    easy_questions: List[str]
    medium_questions: List[str]
    hard_questions: List[str]
    behavioral_questions: List[str]
    system_design_questions: List[str]
    provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewQuestionDeleteResponse(BaseModel):
    message: str


class InterviewQuestionBatchDeleteResponse(BaseModel):
    deleted_count: int
    message: str