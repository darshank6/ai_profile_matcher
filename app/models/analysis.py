from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

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

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False
    )

    candidate_name = Column(
        String(255),
        nullable=True
    )

    candidate_email = Column(
        String(255),
        nullable=True
    )

    resume_text = Column(
        Text,
        nullable=True
    )

    job_description_text = Column(
        Text,
        nullable=True
    )

    extracted_resume_skills = Column(
        Text,
        nullable=True
    )

    extracted_job_skills = Column(
        Text,
        nullable=True
    )

    matched_skills = Column(
        Text,
        nullable=True
    )

    missing_skills = Column(
        Text,
        nullable=True
    )

    strengths = Column(
        Text,
        nullable=True
    )

    recommendations = Column(
        Text,
        nullable=True
    )

    match_score = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="analysis_reports"
    )

    resume = relationship(
        "Resume",
        back_populates="analysis_reports"
    )

    job = relationship(
        "JobDescription",
        back_populates="analysis_reports"
    )