from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestionReport


class InterviewQuestionRepository:
    """
    Repository layer for Interview Question Reports.

    Handles:
    - Create
    - Read
    - Update
    - Delete
    - Search
    - Pagination
    - Batch Delete
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_report(
        self,
        report_data: dict
    ) -> InterviewQuestionReport:
        """
        Create a new interview question report.
        """

        report = InterviewQuestionReport(**report_data)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_report_by_id(
        self,
        report_id: int,
        user_id: int
    ):
        """
        Get a report by ID and validate ownership.
        """

        return (
            self.db.query(InterviewQuestionReport)
            .filter(
                InterviewQuestionReport.id == report_id
            )
            .filter(
                InterviewQuestionReport.user_id == user_id
            )
            .first()
        )

    def get_reports_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List:
        """
        Get paginated reports for a specific user.
        """

        return (
            self.db.query(InterviewQuestionReport)
            .filter(
                InterviewQuestionReport.user_id == user_id
            )
            .order_by(
                InterviewQuestionReport.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_reports(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10
    ) -> List:
        """
        Search reports by title or question content.
        """

        search_pattern = f"%{search}%"

        return (
            self.db.query(InterviewQuestionReport)
            .filter(
                InterviewQuestionReport.user_id == user_id
            )
            .filter(
                or_(
                    InterviewQuestionReport.title.ilike(search_pattern),
                    InterviewQuestionReport.easy_questions.ilike(search_pattern),
                    InterviewQuestionReport.medium_questions.ilike(search_pattern),
                    InterviewQuestionReport.hard_questions.ilike(search_pattern),
                    InterviewQuestionReport.behavioral_questions.ilike(search_pattern),
                    InterviewQuestionReport.system_design_questions.ilike(search_pattern),
                )
            )
            .order_by(
                InterviewQuestionReport.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_report(
        self,
        report: InterviewQuestionReport,
        update_data: dict
    ) -> InterviewQuestionReport:
        """
        Update a report.
        """

        for key, value in update_data.items():
            if value is not None:
                setattr(report, key, value)

        self.db.commit()
        self.db.refresh(report)

        return report

    def delete_report(
        self,
        report: InterviewQuestionReport
    ) -> bool:
        """
        Delete a single report.
        """

        self.db.delete(report)
        self.db.commit()

        return True

    def batch_delete_reports(
        self,
        user_id: int,
        report_ids: List[int]
    ) -> int:
        """
        Delete multiple reports.

        Returns:
            Number of deleted reports.
        """

        reports = (
            self.db.query(InterviewQuestionReport)
            .filter(
                InterviewQuestionReport.user_id == user_id
            )
            .filter(
                InterviewQuestionReport.id.in_(report_ids)
            )
            .all()
        )

        deleted_count = len(reports)

        for report in reports:
            self.db.delete(report)

        self.db.commit()

        return deleted_count