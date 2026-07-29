from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


class CoverLetterReport(Base):
    __tablename__ = "cover_letter_reports"

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

    cover_letter = Column(
        Text,
        nullable=False
    )

    provider = Column(
        String,
        nullable=False
    )

    model_name = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="cover_letter_reports"
    )

    resume = relationship(
        "Resume",
        back_populates="cover_letter_reports"
    )

    job = relationship(
        "JobDescription",
        back_populates="cover_letter_reports"
    )

    