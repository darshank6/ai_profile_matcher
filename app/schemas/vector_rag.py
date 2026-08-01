from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class VectorRAGDocumentCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=255,
        examples=["AI Engineer Notes"],
    )

    content: str = Field(
        ...,
        min_length=20,
        examples=["Python FastAPI PostgreSQL RAG Vector Databases OpenAI Embeddings"],
    )

    source_type: str = Field(
        default="manual",
        max_length=100,
        examples=["manual"],
    )

    source_id: Optional[int] = Field(
        default=None,
        ge=1,
    )

    @field_validator("title", "content", "source_type")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be empty")

        return cleaned_value


class VectorRAGDocumentUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    content: Optional[str] = Field(
        default=None,
        min_length=20,
    )

    @field_validator("title", "content")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be empty")

        return cleaned_value


class VectorRAGDocumentResponse(BaseModel):
    id: int
    user_id: int
    title: str
    source_type: str
    source_id: Optional[int]
    content: str
    chunk_count: int
    embedding_provider: str
    embedding_model: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VectorRAGAskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        examples=["Which skills should I learn for AI Engineer role?"],
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
    def validate_question(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("question cannot be empty")

        return cleaned_value


class VectorRAGQueryReportResponse(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str
    matched_chunks: Optional[str]
    provider: str
    model_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class VectorRAGDeleteResponse(BaseModel):
    message: str


class VectorRAGBatchDeleteRequest(BaseModel):
    document_ids: List[int] = Field(
        ...,
        min_length=1,
        examples=[[1, 2, 3]],
    )

    @field_validator("document_ids")
    @classmethod
    def validate_document_ids(cls, values: List[int]) -> List[int]:
        if any(value <= 0 for value in values):
            raise ValueError("all document_ids must be positive integers")

        return values


class VectorRAGBatchDeleteResponse(BaseModel):
    deleted_count: int
    message: str