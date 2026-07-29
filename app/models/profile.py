from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.database import Base


class UserProfile(Base):

    __tablename__ = "user_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    phone = Column(
        String,
        nullable=True
    )

    location = Column(
        String,
        nullable=True
    )

    current_role = Column(
        String,
        nullable=True
    )

    target_role = Column(
        String,
        nullable=True
    )

    experience_years = Column(
        Integer,
        nullable=True
    )

    linkedin_url = Column(
        String,
        nullable=True
    )

    github_url = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="profile"
    )