from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


class InterviewQuestionReport(Base):
    """
    Stores AI-generated interview question reports for a resume and job description.
    """

    __tablename__ = "interview_question_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=False,
        index=True
    )

    easy_questions = Column(
        Text,
        nullable=False
    )

    medium_questions = Column(
        Text,
        nullable=False
    )

    hard_questions = Column(
        Text,
        nullable=False
    )

    behavioral_questions = Column(
        Text,
        nullable=False
    )

    system_design_questions = Column(
        Text,
        nullable=False
    )

    provider = Column(
        String(50),
        nullable=False
    )

    model_name = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="interview_question_reports"
    )

    resume = relationship(
        "Resume",
        back_populates="interview_question_reports"
    )

    job = relationship(
        "JobDescription",
        back_populates="interview_question_reports"
    )