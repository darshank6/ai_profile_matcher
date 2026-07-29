from sqlalchemy.orm import Session

from app.models.ai_resume_report import AIResumeReport


class AIResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_report(
        self,
        report_data: dict
    ):
        report = AIResumeReport(**report_data)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_report_by_id(
        self,
        report_id: int,
        user_id: int
    ):
        return (
            self.db.query(AIResumeReport)
            .filter(AIResumeReport.id == report_id)
            .filter(AIResumeReport.user_id == user_id)
            .first()
        )

    def get_reports_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ):
        return (
            self.db.query(AIResumeReport)
            .filter(AIResumeReport.user_id == user_id)
            .order_by(AIResumeReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_report(
        self,
        report: AIResumeReport
    ):
        self.db.delete(report)
        self.db.commit()

        return True