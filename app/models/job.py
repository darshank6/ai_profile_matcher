from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from app.database import Base


class JobDescription(Base):

    __tablename__ = "job_descriptions"

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

    title = Column(
        String,
        nullable=False
    )

    company_name = Column(
        String,
        nullable=True
    )

    description = Column(
        Text,
        nullable=False
    )

    required_skills = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="jobs"
    )

    analysis_reports = relationship(
        "AnalysisReport",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    cover_letter_reports = relationship(
        "CoverLetterReport",
        back_populates="job",
        cascade="all, delete-orphan"
    )
    
    interview_question_reports = relationship(
        "InterviewQuestionReport",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    semantic_match_reports = relationship(
        "SemanticMatchReport",
        back_populates="job",
        cascade="all, delete-orphan",
    )