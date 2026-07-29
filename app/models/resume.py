from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    original_filename = Column(
        String,
        nullable=False
    )

    stored_filename = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    file_type = Column(
        String,
        nullable=False
    )

    file_size = Column(
        Integer,
        nullable=False
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )

    analysis_reports = relationship(
        "AnalysisReport",
        back_populates="resume",
        cascade="all, delete-orphan"
    )

    ai_resume_reports = relationship(
        "AIResumeReport",
        back_populates="resume",
        cascade="all, delete-orphan"
    )

    cover_letter_reports = relationship(
        "CoverLetterReport",
        back_populates="resume",
        cascade="all, delete-orphan"

    )

    interview_question_reports = relationship(
        "InterviewQuestionReport",
        back_populates="resume",
        cascade="all, delete-orphan"
    )

    learning_roadmap_reports = relationship(
        "LearningRoadmapReport",
        back_populates="resume",
        cascade="all, delete-orphan"
    )

    job_recommendation_reports = relationship(
        "JobRecommendationReport",
        back_populates="resume",
        cascade="all, delete-orphan"
    )

    semantic_match_reports = relationship(
        "SemanticMatchReport", back_populates="resume", cascade="all, delete-orphan"
    )

