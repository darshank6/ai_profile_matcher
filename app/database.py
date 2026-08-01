from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


# Create the SQLAlchemy engine using the database URL from settings.
engine = create_engine(
    settings.DATABASE_URL
)

# Configure a session factory for creating database sessions.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for declarative models.
Base = declarative_base()


def get_db():
    """Provide a database session generator for dependency injection."""

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
