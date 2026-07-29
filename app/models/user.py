from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from app.database import Base

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="candidate",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False
    )

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    jobs = relationship(
        "JobDescription",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    analysis_reports = relationship(
        "AnalysisReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    ai_resume_reports = relationship(
        "AIResumeReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    cover_letter_reports = relationship(
        "CoverLetterReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    interview_question_reports = relationship(
        "InterviewQuestionReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    learning_roadmap_reports = relationship(
        "LearningRoadmapReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    job_recommendation_reports = relationship(
        "JobRecommendationReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    semantic_match_reports = relationship(
        "SemanticMatchReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    rag_documents = relationship(
        "RAGDocument",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    rag_chunks = relationship(
        "RAGChunk",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    rag_query_reports = relationship(
        "RAGQueryReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )