import json
import logging
from typing import Any
from typing import Dict
from typing import List

from fastapi import HTTPException
from fastapi import status

from app.ai.llm_client import LLMClient
from app.config import settings
from app.repositories.interview_question_repo import InterviewQuestionRepository
from app.repositories.job_repo import JobRepository
from app.repositories.resume_repo import ResumeRepository


logger = logging.getLogger(__name__)


class InterviewQuestionService:
    """
    Service layer for AI Interview Question Generator.

    Responsibility:
    - Validate resume ownership
    - Validate job ownership
    - Validate extracted resume text
    - Validate job description
    - Call LLM client
    - Save generated questions
    - Serialize database reports into API-friendly response
    """

    def __init__(
        self,
        db
    ) -> None:
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.interview_repo = InterviewQuestionRepository(db)

    def generate_interview_questions(
        self,
        user_id: int,
        resume_id: int,
        job_id: int,
        provider: str | None = None,
        model_name: str | None = None
    ) -> Dict[str, Any]:
        """
        Generate AI interview questions using resume and job description.
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
                detail="Resume does not contain extracted text"
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

        if not job_description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is empty"
            )

        final_provider = provider or settings.LLM_PROVIDER
        final_model_name = model_name or settings.LLM_MODEL

        llm_client = LLMClient(
            provider=final_provider,
            model_name=final_model_name
        )

        questions = llm_client.generate_interview_questions(
            resume_text=resume_text,
            job_title=job.title,
            company_name=job.company_name,
            job_description=job_description
        )

        normalized_questions = self._normalize_questions(
            questions
        )

        report_title = f"Interview Questions for {job.title}"

        report_data = {
            "user_id": user_id,
            "resume_id": resume.id,
            "job_id": job.id,
            "title": report_title,
            "easy_questions": json.dumps(
                normalized_questions["easy_questions"]
            ),
            "medium_questions": json.dumps(
                normalized_questions["medium_questions"]
            ),
            "hard_questions": json.dumps(
                normalized_questions["hard_questions"]
            ),
            "behavioral_questions": json.dumps(
                normalized_questions["behavioral_questions"]
            ),
            "system_design_questions": json.dumps(
                normalized_questions["system_design_questions"]
            ),
            "provider": final_provider,
            "model_name": final_model_name
        }

        report = self.interview_repo.create_report(
            report_data
        )

        logger.info(
            "Interview questions generated successfully | user_id=%s resume_id=%s job_id=%s report_id=%s",
            user_id,
            resume_id,
            job_id,
            report.id
        )

        return self._serialize_report(report)

    def get_my_reports(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Return paginated interview question reports for the logged-in user.
        """

        reports = self.interview_repo.get_reports_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

        return [
            self._serialize_report(report)
            for report in reports
        ]

    def get_report(
        self,
        report_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Return one interview question report.
        """

        report = self.interview_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview question report not found"
            )

        return self._serialize_report(report)

    def search_reports(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search interview question reports.
        """

        cleaned_search = search.strip()

        if not cleaned_search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )

        reports = self.interview_repo.search_reports(
            user_id=user_id,
            search=cleaned_search,
            skip=skip,
            limit=limit
        )

        return [
            self._serialize_report(report)
            for report in reports
        ]

    def update_report(
        self,
        report_id: int,
        user_id: int,
        update_data: dict
    ) -> Dict[str, Any]:
        """
        Update an interview question report.

        Currently supports title update.
        """

        report = self.interview_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview question report not found"
            )

        updated_report = self.interview_repo.update_report(
            report=report,
            update_data=update_data
        )

        logger.info(
            "Interview question report updated | report_id=%s user_id=%s",
            report_id,
            user_id
        )

        return self._serialize_report(updated_report)

    def delete_report(
        self,
        report_id: int,
        user_id: int
    ) -> Dict[str, str]:
        """
        Delete one interview question report.
        """

        report = self.interview_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview question report not found"
            )

        self.interview_repo.delete_report(
            report
        )

        logger.info(
            "Interview question report deleted | report_id=%s user_id=%s",
            report_id,
            user_id
        )

        return {
            "message": "Interview question report deleted successfully"
        }

    def batch_delete_reports(
        self,
        user_id: int,
        report_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Delete multiple interview question reports.
        """

        if not report_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report_ids cannot be empty"
            )

        deleted_count = self.interview_repo.batch_delete_reports(
            user_id=user_id,
            report_ids=report_ids
        )

        logger.info(
            "Batch deleted interview question reports | user_id=%s deleted_count=%s",
            user_id,
            deleted_count
        )

        return {
            "deleted_count": deleted_count,
            "message": f"{deleted_count} interview question report(s) deleted successfully"
        }

    def _serialize_report(
        self,
        report
    ) -> Dict[str, Any]:
        """
        Convert SQLAlchemy model into API-friendly dictionary.

        JSON string columns are converted back into Python lists.
        """

        return {
            "id": report.id,
            "user_id": report.user_id,
            "resume_id": report.resume_id,
            "job_id": report.job_id,
            "title": report.title,
            "easy_questions": self._json_to_list(
                report.easy_questions
            ),
            "medium_questions": self._json_to_list(
                report.medium_questions
            ),
            "hard_questions": self._json_to_list(
                report.hard_questions
            ),
            "behavioral_questions": self._json_to_list(
                report.behavioral_questions
            ),
            "system_design_questions": self._json_to_list(
                report.system_design_questions
            ),
            "provider": report.provider,
            "model_name": report.model_name,
            "created_at": report.created_at,
            "updated_at": report.updated_at
        }

    def _json_to_list(
        self,
        value: str | None
    ) -> List:
        """
        Convert JSON string from database into list of strings.
        """

        if value is None:
            return []

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return [
                    str(item)
                    for item in parsed
                ]

            if isinstance(parsed, str):
                return [
                    parsed
                ]

            return [
                str(parsed)
            ]

        except Exception:
            logger.exception(
                "Failed to parse interview question JSON value."
            )

            return []

    def _normalize_questions(
        self,
        questions: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Ensure all expected question categories exist and are lists.
        """

        return {
            "easy_questions": self._ensure_list(
                questions.get("easy_questions")
            ),
            "medium_questions": self._ensure_list(
                questions.get("medium_questions")
            ),
            "hard_questions": self._ensure_list(
                questions.get("hard_questions")
            ),
            "behavioral_questions": self._ensure_list(
                questions.get("behavioral_questions")
            ),
            "system_design_questions": self._ensure_list(
                questions.get("system_design_questions")
            ),
        }

    def _ensure_list(
        self,
        value: Any
    ) -> List:
        """
        Convert any LLM value into a clean list of strings.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return [
                str(item)
                for item in value
            ]

        if isinstance(value, str):
            return [
                value
            ]

        return [
            str(value)
        ]