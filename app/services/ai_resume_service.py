from fastapi import HTTPException
from fastapi import status

from app.ai.llm_client import LLMClient
from app.config import settings
from app.repositories.ai_resume_repo import AIResumeRepository
from app.repositories.resume_repo import ResumeRepository


class AIResumeService:
    def __init__(self, db):
        self.resume_repo = ResumeRepository(db)
        self.ai_resume_repo = AIResumeRepository(db)

    def analyze_resume(
        self,
        user_id: int,
        resume_id: int,
        provider: str | None = None,
        model_name: str | None = None
    ):
        resume = self.resume_repo.get_resume_by_id(
            resume_id=resume_id,
            user_id=user_id
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        resume_text = resume.extracted_text or ""

        if not resume_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume does not contain extracted text"
            )

        final_provider = provider or settings.LLM_PROVIDER
        final_model = model_name or settings.LLM_MODEL

        llm_client = LLMClient(
            provider=final_provider,
            model_name=final_model
        )

        ai_result = llm_client.generate_resume_analysis(
            resume_text=resume_text
        )

        report_data = {
            "user_id": user_id,
            "resume_id": resume.id,
            "summary": ai_result["summary"],
            "strengths": ai_result["strengths"],
            "weaknesses": ai_result["weaknesses"],
            "suggestions": ai_result["suggestions"],
            "provider": final_provider,
            "model_name": final_model
        }

        return self.ai_resume_repo.create_report(report_data)

    def get_my_reports(
        self,
        user_id: int,
        skip: int,
        limit: int
    ):
        return self.ai_resume_repo.get_reports_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    def get_report(
        self,
        report_id: int,
        user_id: int
    ):
        report = self.ai_resume_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI resume report not found"
            )

        return report

    def delete_report(
        self,
        report_id: int,
        user_id: int
    ):
        report = self.ai_resume_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI resume report not found"
            )

        self.ai_resume_repo.delete_report(report)

        return {
            "message": "AI resume report deleted successfully"
        }