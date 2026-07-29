from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class SemanticMatchGenerateRequest(BaseModel):
    """
    Request schema for generating semantic ATS match report.
    """

    resume_id: int = Field(
        ...,
        gt=0,
        examples=[2],
        description="Resume ID used for semantic matching.",
    )

    job_id: int = Field(
        ...,
        gt=0,
        examples=[1],
        description="Job description ID used for semantic matching.",
    )


class SemanticMatchUpdateRequest(BaseModel):
    """
    Request schema for updating editable text fields of a semantic match report.
    """

    match_explanation: Optional[str] = Field(
        default=None,
        examples=["Updated semantic explanation."],
    )

    recommendation: Optional[str] = Field(
        default=None,
        examples=["Improve Docker and Kubernetes project experience."],
    )

    @field_validator("match_explanation")
    @classmethod
    def validate_match_explanation(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("match_explanation cannot be empty")

        return cleaned_value

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("recommendation cannot be empty")

        return cleaned_value


class SemanticMatchResponse(BaseModel):
    """
    Response schema for semantic match reports.
    """

    id: int
    user_id: int
    resume_id: int
    job_id: int
    keyword_score: float
    semantic_score: float
    overall_score: float
    resume_skills: List[str]
    job_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    match_explanation: Optional[str]
    recommendation: Optional[str]
    provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SemanticMatchDeleteResponse(BaseModel):
    """
    Response schema for deleting one semantic match report.
    """

    message: str


class SemanticMatchBatchDeleteRequest(BaseModel):
    """
    Request schema for batch deleting semantic match reports.
    """

    report_ids: List[int] = Field(
        ...,
        min_length=1,
        examples=[[1, 2, 3]],
    )

    @field_validator("report_ids")
    @classmethod
    def validate_report_ids(
        cls,
        values: List[int],
    ) -> List[int]:
        if any(value <= 0 for value in values):
            raise ValueError("all report_ids must be positive integers")

        return values


class SemanticMatchBatchDeleteResponse(BaseModel):
    """
    Response schema for batch delete operation.
    """

    deleted_count: int
    message: str