from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


class LearningRoadmapReport(Base):
    """
    Stores AI-generated personalized learning roadmaps.

    A learning roadmap is generated for a logged-in user based on:
    - Uploaded resume
    - Target role
    - Skill gaps
    - AI recommendations
    """

    __tablename__ = "learning_roadmap_reports"

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
        nullable=False,
        index=True
    )

    current_skills = Column(
        Text,
        nullable=True
    )

    missing_skills = Column(
        Text,
        nullable=True
    )

    roadmap_title = Column(
        Text,
        nullable=True
    )

    roadmap_summary = Column(
        Text,
        nullable=False
    )

    weekly_plan = Column(
        Text,
        nullable=False
    )

    recommended_projects = Column(
        Text,
        nullable=True
    )

    recommended_courses = Column(
        Text,
        nullable=True
    )

    recommended_certifications = Column(
        Text,
        nullable=True
    )

    priority_topics = Column(
        Text,
        nullable=True
    )

    estimated_duration = Column(
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
        back_populates="learning_roadmap_reports"
    )

    resume = relationship(
        "Resume",
        back_populates="learning_roadmap_reports"
    )