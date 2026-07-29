from sqlalchemy.orm import Session

from app.models.analysis import AnalysisReport


class ATSRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_report(self, report_data: dict):

        report = AnalysisReport(
            **report_data
        )

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
            self.db.query(
                AnalysisReport
            )
            .filter(
                AnalysisReport.id == report_id
            )
            .filter(
                AnalysisReport.user_id == user_id
            )
            .first()
        )

    def get_reports_by_user(
        self,
        user_id: int,
        skip=int,
        limit=int
    ):

        return (
            self.db.query(
                AnalysisReport
            )
            .filter(
                AnalysisReport.user_id == user_id
            )
            .order_by(
                AnalysisReport.created_at.desc()
            )
            .all()
        )

    def delete_report(
        self,
        report: AnalysisReport
    ):

        self.db.delete(report)

        self.db.commit()

        return True