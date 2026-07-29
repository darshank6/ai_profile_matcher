from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class JobRecommendationGenerateRequest(BaseModel):
    resume_id: int = Field(
        ...,
        gt=0,
        examples=[2],
        description="Resume ID used for job recommendation."
    )

    target_role: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["Python Backend Developer"],
        description="Optional target role to guide recommendations."
    )

    provider: Optional[str] = Field(
        default=None,
        examples=["ollama"],
        description="LLM provider. Supported: ollama, openai."
    )

    model_name: Optional[str] = Field(
        default=None,
        examples=["llama3"],
        description="LLM model name."
    )

    top_n: int = Field(
        default=5,
        ge=1,
        le=20,
        examples=[5],
        description="Number of top jobs to recommend."
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip().lower()

        if cleaned_value not in {"ollama", "openai"}:
            raise ValueError("provider must be either 'ollama' or 'openai'")

        return cleaned_value

    @field_validator("target_role")
    @classmethod
    def validate_target_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("target_role cannot be empty")

        return cleaned_value


class JobRecommendationUpdateRequest(BaseModel):
    target_role: Optional[str] = Field(
        default=None,
        max_length=255
    )

    recommendation_summary: Optional[str] = Field(
        default=None
    )

    @field_validator("target_role")
    @classmethod
    def validate_target_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("target_role cannot be empty")

        return cleaned_value


class RecommendedJobItem(BaseModel):
    job_id: int
    title: str
    company_name: Optional[str]
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]


class JobRecommendationResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    target_role: Optional[str]
    resume_skills: Optional[str]
    recommended_jobs: List[RecommendedJobItem]
    missing_skills_summary: Optional[str]
    recommendation_summary: Optional[str]
    provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobRecommendationDeleteResponse(BaseModel):
    message: str


class JobRecommendationBatchDeleteRequest(BaseModel):
    report_ids: List[int] = Field(
        ...,
        min_length=1,
        examples=[[1, 2, 3]]
    )

    @field_validator("report_ids")
    @classmethod
    def validate_report_ids(cls, values: List[int]) -> List[int]:
        if any(value <= 0 for value in values):
            raise ValueError("all report_ids must be positive integers")

        return values


class JobRecommendationBatchDeleteResponse(BaseModel):
    deleted_count: int
    message: str