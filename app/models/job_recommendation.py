from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


class JobRecommendationReport(Base):
    """
    Stores AI-generated job recommendation reports.

    A single report is generated for one resume and contains
    a JSON list of recommended jobs with match scores.
    """

    __tablename__ = "job_recommendation_reports"

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

    target_role = Column(
        String(255),
        nullable=True,
        index=True
    )

    resume_skills = Column(
        Text,
        nullable=True
    )

    recommended_jobs = Column(
        Text,
        nullable=False
    )

    missing_skills_summary = Column(
        Text,
        nullable=True
    )

    recommendation_summary = Column(
        Text,
        nullable=True
    )

    provider = Column(
        String(50),
        nullable=False
    )

    model_name = Column(
        String(255),
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
        back_populates="job_recommendation_reports"
    )

    resume = relationship(
        "Resume",
        back_populates="job_recommendation_reports"
    )