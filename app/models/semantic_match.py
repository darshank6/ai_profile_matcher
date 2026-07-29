from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


class SemanticMatchReport(Base):
    """
    SQLAlchemy model for advanced semantic ATS matching reports.

    This report stores:
    - Keyword skill score
    - Semantic similarity score
    - Overall weighted score
    - Extracted resume skills
    - Extracted job skills
    - Matched skills
    - Missing skills
    - Explanation and recommendation text
    """

    __tablename__ = "semantic_match_reports"

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

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False,
        index=True,
    )

    job_id = Column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
        index=True,
    )

    keyword_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True,
    )

    semantic_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True,
    )

    overall_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True,
    )

    resume_skills = Column(
        Text,
        nullable=True,
    )

    job_skills = Column(
        Text,
        nullable=True,
    )

    matched_skills = Column(
        Text,
        nullable=True,
    )

    missing_skills = Column(
        Text,
        nullable=True,
    )

    match_explanation = Column(
        Text,
        nullable=True,
    )

    recommendation = Column(
        Text,
        nullable=True,
    )

    provider = Column(
        Text,
        nullable=False,
        default="local",
    )

    model_name = Column(
        Text,
        nullable=False,
        default="token-cosine-semantic-v1",
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
        back_populates="semantic_match_reports",
    )

    resume = relationship(
        "Resume",
        back_populates="semantic_match_reports",
    )

    job = relationship(
        "JobDescription",
        back_populates="semantic_match_reports",
    )