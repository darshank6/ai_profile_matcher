from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


class CareerCoachSession(Base):
    """
    Career coach chat session.
    """

    __tablename__ = "career_coach_sessions"

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

    target_role = Column(
        String(255),
        nullable=True,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
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
        back_populates="career_coach_sessions",
    )

    messages = relationship(
        "CareerCoachMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class CareerCoachMessage(Base):
    """
    Career coach chat message.
    """

    __tablename__ = "career_coach_messages"

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

    session_id = Column(
        Integer,
        ForeignKey("career_coach_sessions.id"),
        nullable=False,
        index=True,
    )

    role = Column(
        String(50),
        nullable=False,
        index=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    context_chunks = Column(
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
        back_populates="career_coach_messages",
    )

    session = relationship(
        "CareerCoachSession",
        back_populates="messages",
    )