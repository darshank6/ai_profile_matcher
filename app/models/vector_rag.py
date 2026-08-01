from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.config import settings
from app.database import Base


class VectorRAGDocument(Base):
    """
    Stores user-owned documents for PgVector-backed RAG.
    """

    __tablename__ = "vector_rag_documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
        index=True,
    )

    source_type = Column(
        String(100),
        nullable=False,
        default="manual",
        index=True,
    )

    source_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    chunk_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    embedding_provider = Column(
        String(100),
        nullable=False,
        default="openai-proxy",
    )

    embedding_model = Column(
        String(255),
        nullable=False,
        default="kgpt-text-embedding",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="vector_rag_documents",
    )

    chunks = relationship(
        "VectorRAGChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class VectorRAGChunk(Base):
    """
    Stores individual document chunks with native pgvector embeddings.
    """

    __tablename__ = "vector_rag_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey("vector_rag_documents.id"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
        index=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    token_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    embedding = Column(
        Vector(settings.EMBEDDING_VECTOR_SIZE),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="vector_rag_chunks",
    )

    document = relationship(
        "VectorRAGDocument",
        back_populates="chunks",
    )


class VectorRAGQueryReport(Base):
    """
    Stores PgVector RAG question-answer history.
    """

    __tablename__ = "vector_rag_query_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    question = Column(
        Text,
        nullable=False,
    )

    answer = Column(
        Text,
        nullable=False,
    )

    matched_chunks = Column(
        Text,
        nullable=True,
    )

    provider = Column(
        String(50),
        nullable=False,
        default="openai",
    )

    model_name = Column(
        String(255),
        nullable=False,
        default="kgpt-reasoning-text",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="vector_rag_query_reports",
    )