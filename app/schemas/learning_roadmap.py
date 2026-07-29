from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class LearningRoadmapGenerateRequest(BaseModel):
    """
    Request schema for generating an AI learning roadmap.
    """

    resume_id: int = Field(
        ...,
        gt=0,
        examples=[2],
        description="Resume ID for which roadmap should be generated."
    )

    target_role: str = Field(
        ...,
        min_length=2,
        max_length=255,
        examples=["AI Engineer"],
        description="Target role for which roadmap should be generated."
    )

    provider: Optional[str] = Field(
        default='openai',
        examples=["ollama"],
        description="LLM provider. Supported values: ollama, openai."
    )

    model_name: Optional[str] = Field(
        default='kgpt-reasoning-text',
        examples=["llama3"],
        description="LLM model name."
    )

    @field_validator("target_role")
    @classmethod
    def validate_target_role(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("target_role cannot be empty")

        return cleaned_value

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        allowed_providers = {
            "ollama",
            "openai"
        }

        cleaned_value = value.strip().lower()

        if cleaned_value not in allowed_providers:
            raise ValueError("provider must be either 'ollama' or 'openai'")

        return cleaned_value


class LearningRoadmapUpdateRequest(BaseModel):
    """
    Request schema for updating basic roadmap metadata.
    """

    roadmap_title: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["AI Engineer Roadmap - 12 Weeks"]
    )

    estimated_duration: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["12 weeks"]
    )

    @field_validator("roadmap_title")
    @classmethod
    def validate_roadmap_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("roadmap_title cannot be empty")

        return cleaned_value

    @field_validator("estimated_duration")
    @classmethod
    def validate_estimated_duration(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("estimated_duration cannot be empty")

        return cleaned_value


class LearningRoadmapBatchDeleteRequest(BaseModel):
    """
    Request schema for deleting multiple learning roadmap reports.
    """

    roadmap_ids: List[int] = Field(
        ...,
        min_length=1,
        examples=[[1, 2, 3]]
    )

    @field_validator("roadmap_ids")
    @classmethod
    def validate_roadmap_ids(cls, values: List[int]) -> List[int]:
        if any(value <= 0 for value in values):
            raise ValueError("all roadmap ids must be positive integers")

        return values


class LearningRoadmapResponse(BaseModel):
    """
    Response schema for a learning roadmap report.
    """

    id: int
    user_id: int
    resume_id: int
    target_role: str
    current_skills: Optional[str]
    missing_skills: Optional[str]
    roadmap_title: str
    roadmap_summary: str
    weekly_plan: str
    recommended_projects: Optional[str]
    recommended_courses: Optional[str]
    recommended_certifications: Optional[str]
    priority_topics: Optional[str]
    estimated_duration: Optional[str]
    provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningRoadmapDeleteResponse(BaseModel):
    """
    Delete response schema.
    """

    message: str


class LearningRoadmapBatchDeleteResponse(BaseModel):
    """
    Batch delete response schema.
    """

    deleted_count: int
    message: str