from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_resume(
        self,
        resume_data: dict
    ):
        resume = Resume(**resume_data)

        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)

        return resume

    def get_resume_by_id(
        self,
        resume_id: int,
        user_id: int
    ):
        return (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .filter(Resume.user_id == user_id)
            .first()
        )

    def get_user_resumes(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ):
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_resume(
        self,
        resume: Resume
    ):
        self.db.delete(resume)
        self.db.commit()

        return True