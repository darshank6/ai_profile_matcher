from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.learning_roadmap import LearningRoadmapReport


class LearningRoadmapRepository:
    """
    Repository layer for LearningRoadmapReport.

    Responsibility:
    - Create learning roadmap reports
    - Get one roadmap by id
    - Get all user roadmaps with pagination
    - Search roadmaps
    - Filter roadmaps by target role
    - Update roadmap metadata/content
    - Delete one roadmap
    - Batch delete roadmaps

    This layer must only contain database access logic.
    Business rules must stay inside the service layer.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize repository with SQLAlchemy database session.
        """

        self.db = db

    def create_roadmap(
        self,
        roadmap_data: dict
    ) -> LearningRoadmapReport:
        """
        Create and persist a new learning roadmap report.

        Args:
            roadmap_data: Dictionary containing roadmap fields.

        Returns:
            Newly created LearningRoadmapReport object.
        """

        roadmap = LearningRoadmapReport(**roadmap_data)

        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)

        return roadmap

    def get_roadmap_by_id(
        self,
        roadmap_id: int,
        user_id: int
    ) :
        """
        Get one roadmap by ID and user ID.

        This ensures users can only access their own roadmap reports.

        Args:
            roadmap_id: Learning roadmap primary key.
            user_id: Logged-in user's ID.

        Returns:
            LearningRoadmapReport object if found, otherwise None.
        """

        return (
            self.db.query(LearningRoadmapReport)
            .filter(LearningRoadmapReport.id == roadmap_id)
            .filter(LearningRoadmapReport.user_id == user_id)
            .first()
        )

    def get_roadmaps_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) :
        """
        Get paginated learning roadmap reports for a user.

        Args:
            user_id: Logged-in user's ID.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of LearningRoadmapReport objects.
        """

        return (
            self.db.query(LearningRoadmapReport)
            .filter(LearningRoadmapReport.user_id == user_id)
            .order_by(LearningRoadmapReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_roadmaps(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10
    ) : 
        """
        Search learning roadmaps by target role, title, summary,
        missing skills, priority topics, projects, courses, or certifications.

        Args:
            user_id: Logged-in user's ID.
            search: Search keyword.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of matching LearningRoadmapReport objects.
        """

        search