import logging

from fastapi import HTTPException
from fastapi import status

from app.ai.llm_client import LLMClient
from app.config import settings

from app.repositories.cover_letter_repo import (
    CoverLetterRepository
)

from app.repositories.job_repo import (
    JobRepository
)

from app.repositories.resume_repo import (
    ResumeRepository
)


logger = logging.getLogger(__name__)


class CoverLetterService:
    """
    Business logic layer for AI cover letters.
    """

    def __init__(self, db):
        self.resume_repo = ResumeRepository(db)

        self.job_repo = JobRepository(db)

        self.cover_letter_repo = CoverLetterRepository(
            db
        )

    def generate_cover_letter(
        self,
        user_id: int,
        resume_id: int,
        job_id: int,
        provider: str | None = None,
        model_name: str | None = None
    ):
        """
        Generate AI cover letter and save it.
        """

        resume = self.resume_repo.get_resume_by_id(
            resume_id=resume_id,
            user_id=user_id
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        job = self.job_repo.get_job_by_id(
            job_id=job_id,
            user_id=user_id
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        resume_text = (
            resume.extracted_text or ""
        ).strip()

        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume text not available"
            )

        job_description = (
            job.description or ""
        ).strip()

        if job.required_skills:
            job_description = (
                job_description
                + "\n\nRequired Skills:\n"
                + job.required_skills
            )

        if not job_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is empty"
            )

        final_provider = (
            provider
            or settings.LLM_PROVIDER
        )

        final_model_name = (
            model_name
            or settings.LLM_MODEL
        )

        logger.info(
            "Generating cover letter | user_id=%s resume_id=%s job_id=%s",
            user_id,
            resume_id,
            job_id
        )

        llm_client = LLMClient(
            provider=final_provider,
            model_name=final_model_name
        )

        generated_cover_letter = (
            llm_client.generate_cover_letter(
                resume_text=resume_text,
                job_title=job.title,
                company_name=job.company_name,
                job_description=job_description
            )
        )

        report_data = {
            "user_id": user_id,
            "resume_id": resume.id,
            "job_id": job.id,
            "cover_letter": generated_cover_letter,
            "provider": final_provider,
            "model_name": final_model_name
        }

        saved_cover_letter = (
            self.cover_letter_repo.create_cover_letter(
                report_data
            )
        )

        logger.info(
            "Cover letter generated successfully | report_id=%s",
            saved_cover_letter.id
        )

        return saved_cover_letter

    def get_my_cover_letters(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ):
        """
        Return user cover letters.
        """

        return (
            self.cover_letter_repo.get_cover_letters_by_user(
                user_id=user_id,
                skip=skip,
                limit=limit
            )
        )

    def get_cover_letter(
        self,
        cover_letter_id: int,
        user_id: int
    ):
        """
        Return one cover letter.
        """

        cover_letter = (
            self.cover_letter_repo.get_cover_letter_by_id(
                cover_letter_id=cover_letter_id,
                user_id=user_id
            )
        )

        if not cover_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found"
            )

        return cover_letter

    def delete_cover_letter(
        self,
        cover_letter_id: int,
        user_id: int
    ):
        """
        Delete a cover letter.
        """

        cover_letter = (
            self.cover_letter_repo.get_cover_letter_by_id(
                cover_letter_id=cover_letter_id,
                user_id=user_id
            )
        )

        if not cover_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found"
            )

        self.cover_letter_repo.delete_cover_letter(
            cover_letter
        )

        logger.info(
            "Cover letter deleted | cover_letter_id=%s",
            cover_letter_id
        )

        return {
            "message": "Cover letter deleted successfully"
        }