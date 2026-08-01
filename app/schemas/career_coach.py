from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class CareerCoachSessionCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=255,
        examples=["AI Engineer Career Plan"],
    )

    target_role: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["AI Engineer"],
    )

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("title cannot be empty")

        return cleaned_value


class CareerCoachSessionUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    target_role: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    is_active: Optional[bool] = Field(
        default=None,
    )


class CareerCoachAskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        examples=["How can I become an AI Engineer in 6 months?"],
    )

    session_id: Optional[int] = Field(
        default=None,
        ge=1,
    )

    target_role: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["AI Engineer"],
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    provider: Optional[str] = Field(
        default=None,
        examples=["openai"],
    )

    model_name: Optional[str] = Field(
        default=None,
        examples=["kgpt-reasoning-text"],
    )

    @field_validator("question")
    @classmethod
    def validate_question(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("question cannot be empty")

        return cleaned_value


class CareerCoachSessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    target_role: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CareerCoachMessageResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    role: str
    content: str
    context_chunks: Optional[str]
    provider: str
    model_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CareerCoachAskResponse(BaseModel):
    session: CareerCoachSessionResponse
    user_message: CareerCoachMessageResponse
    assistant_message: CareerCoachMessageResponse


class CareerCoachDeleteResponse(BaseModel):
    message: str


class CareerCoachBatchDeleteRequest(BaseModel):
    session_ids: list[int] = Field(
        ...,
        min_length=1,
        examples=[[1, 2, 3]],
    )

    @field_validator("session_ids")
    @classmethod
    def validate_session_ids(
        cls,
        values: list[int],
    ) -> list[int]:
        if any(value <= 0 for value in values):
            raise ValueError("all session_ids must be positive integers")

        return values


class CareerCoachBatchDeleteResponse(BaseModel):
    deleted_count: int
    message: str