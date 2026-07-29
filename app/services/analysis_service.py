from fastapi import HTTPException

from app.ai.skill_extractor import (
    extract_skills
)

from app.repositories.resume_repo import (
    ResumeRepository
)


class AnalysisService:

    def __init__(self, db):

        self.resume_repo = ResumeRepository(
            db
        )

    def extract_resume_skills(
        self,
        user_id: int,
        resume_id: int
    ):

        resume = (
            self.resume_repo
            .get_resume_by_id(
                resume_id,
                user_id
            )
        )

        if not resume:

            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        skills = extract_skills(
            resume.extracted_text or ""
        )

        return {
            "skills": skills
        }