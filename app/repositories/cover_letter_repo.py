from typing import List
from typing import Optional

from sqlalchemy.orm import Session

from app.models.cover_letter import CoverLetterReport


class CoverLetterRepository:
    """
    Repository layer for CoverLetterReport.

    This class is responsible only for database operations.
    It should not contain business logic.
    Business logic belongs inside the service layer.
    """

    def __init__(
        self,
        db: Session
    ) -> None:
        """
        Initialize repository with SQLAlchemy database session.
        """

        self.db = db

    def create_cover_letter(
        self,
        cover_letter_data: dict
    ) -> CoverLetterReport:
        """
        Create and save a new cover letter record in the database.

        Args:
            cover_letter_data: Dictionary containing cover letter fields.

        Returns:
            Newly created CoverLetterReport object.
        """

        cover_letter = CoverLetterReport(
            **cover_letter_data
        )

        self.db.add(cover_letter)
        self.db.commit()
        self.db.refresh(cover_letter)

        return cover_letter

    def get_cover_letter_by_id(
        self,
        cover_letter_id: int,
        user_id: int
    ):
        """
        Get a single cover letter by ID and user ID.

        This ensures users can only access their own cover letters.

        Args:
            cover_letter_id: Cover letter primary key.
            user_id: Logged-in user's ID.

        Returns:
            CoverLetterReport object if found, otherwise None.
        """

        return (
            self.db.query(CoverLetterReport)
            .filter(
                CoverLetterReport.id == cover_letter_id
            )
            .filter(
                CoverLetterReport.user_id == user_id
            )
            .first()
        )

    def get_cover_letters_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List:
        """
        Get paginated cover letters for a logged-in user.

        Args:
            user_id: Logged-in user's ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of CoverLetterReport objects.
        """

        return (
            self.db.query(CoverLetterReport)
            .filter(
                CoverLetterReport.user_id == user_id
            )
            .order_by(
                CoverLetterReport.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_cover_letter(
        self,
        cover_letter: CoverLetterReport
    ) -> bool:
        """
        Delete a cover letter record.

        Args:
            cover_letter: CoverLetterReport object to delete.

        Returns:
            True after successful deletion.
        """

        self.db.delete(cover_letter)
        self.db.commit()

        return True