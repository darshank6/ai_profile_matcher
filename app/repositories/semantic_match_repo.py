from typing import List
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.semantic_match import SemanticMatchReport


class SemanticMatchRepository:
    """
    Repository layer for SemanticMatchReport.

    This class should contain only SQLAlchemy database operations.
    Business logic belongs in the service layer.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create_report(
        self,
        report_data: dict,
    ) -> SemanticMatchReport:
        """
        Create and persist a semantic match report.
        """

        report = SemanticMatchReport(**report_data)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_report_by_id(
        self,
        report_id: int,
        user_id: int,
    ) -> Optional[SemanticMatchReport]:
        """
        Get a semantic match report by ID and user ownership.
        """

        return (
            self.db.query(SemanticMatchReport)
            .filter(SemanticMatchReport.id == report_id)
            .filter(SemanticMatchReport.user_id == user_id)
            .first()
        )

    def get_reports_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[SemanticMatchReport]:
        """
        Get paginated semantic match reports for a user.
        """

        return (
            self.db.query(SemanticMatchReport)
            .filter(SemanticMatchReport.user_id == user_id)
            .order_by(SemanticMatchReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_reports(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10,
    ) -> List[SemanticMatchReport]:
        """
        Search semantic reports by skills, explanation, or recommendation.
        """

        search_pattern = f"%{search}%"

        return (
            self.db.query(SemanticMatchReport)
            .filter(SemanticMatchReport.user_id == user_id)
            .filter(
                or_(
                    SemanticMatchReport.resume_skills.ilike(search_pattern),
                    SemanticMatchReport.job_skills.ilike(search_pattern),
                    SemanticMatchReport.matched_skills.ilike(search_pattern),
                    SemanticMatchReport.missing_skills.ilike(search_pattern),
                    SemanticMatchReport.match_explanation.ilike(search_pattern),
                    SemanticMatchReport.recommendation.ilike(search_pattern),
                )
            )
            .order_by(SemanticMatchReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_report(
        self,
        report: SemanticMatchReport,
        update_data: dict,
    ) -> SemanticMatchReport:
        """
        Update editable fields of a semantic match report.
        """

        for key, value in update_data.items():
            if value is not None:
                setattr(report, key, value)

        self.db.commit()
        self.db.refresh(report)

        return report

    def delete_report(
        self,
        report: SemanticMatchReport,
    ) -> bool:
        """
        Delete one semantic match report.
        """

        self.db.delete(report)
        self.db.commit()

        return True

    def batch_delete_reports(
        self,
        user_id: int,
        report_ids: List[int],
    ) -> int:
        """
        Delete multiple semantic match reports owned by a user.
        """

        reports = (
            self.db.query(SemanticMatchReport)
            .filter(SemanticMatchReport.user_id == user_id)
            .filter(SemanticMatchReport.id.in_(report_ids))
            .all()
        )

        deleted_count = len(reports)

        for report in reports:
            self.db.delete(report)

        self.db.commit()

        return deleted_count