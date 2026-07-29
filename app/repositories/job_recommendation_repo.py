from typing import List
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.job_recommendation import JobRecommendationReport


class JobRecommendationRepository:
    """
    Repository for JobRecommendationReport database operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_report(
        self,
        report_data: dict
    ) -> JobRecommendationReport:
        report = JobRecommendationReport(**report_data)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_report_by_id(
        self,
        report_id: int,
        user_id: int
    ) -> Optional[JobRecommendationReport]:
        return (
            self.db.query(JobRecommendationReport)
            .filter(JobRecommendationReport.id == report_id)
            .filter(JobRecommendationReport.user_id == user_id)
            .first()
        )

    def get_reports_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[JobRecommendationReport]:
        return (
            self.db.query(JobRecommendationReport)
            .filter(JobRecommendationReport.user_id == user_id)
            .order_by(JobRecommendationReport.created_at.desc())
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
        search_pattern = f"%{search}%"

        return (
            self.db.query(JobRecommendationReport)
            .filter(JobRecommendationReport.user_id == user_id)
            .filter(
                or_(
                    JobRecommendationReport.target_role.ilike(search_pattern),
                    JobRecommendationReport.resume_skills.ilike(search_pattern),
                    JobRecommendationReport.recommended_jobs.ilike(search_pattern),
                    JobRecommendationReport.missing_skills_summary.ilike(search_pattern),
                    JobRecommendationReport.recommendation_summary.ilike(search_pattern),
                )
            )
            .order_by(JobRecommendationReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_report(
        self,
        report: JobRecommendationReport,
        update_data: dict
    ) -> JobRecommendationReport:
        for key, value in update_data.items():
            if value is not None:
                setattr(report, key, value)

        self.db.commit()
        self.db.refresh(report)

        return report

    def delete_report(
        self,
        report: JobRecommendationReport
    ) -> bool:
        self.db.delete(report)
        self.db.commit()

        return True

    def batch_delete_reports(
        self,
        user_id: int,
        report_ids: List[int]
    ) -> int:
        reports = (
            self.db.query(JobRecommendationReport)
            .filter(JobRecommendationReport.user_id == user_id)
            .filter(JobRecommendationReport.id.in_(report_ids))
            .all()
        )

        deleted_count = len(reports)

        for report in reports:
            self.db.delete(report)

        self.db.commit()

        return deleted_count