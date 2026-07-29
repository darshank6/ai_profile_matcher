import json
import logging
from typing import Any
from typing import Dict
from typing import List

from fastapi import HTTPException
from fastapi import status

from app.ai.llm_client import LLMClient
from app.ai.skill_extractor import extract_skills
from app.config import settings
from app.repositories.job_recommendation_repo import JobRecommendationRepository
from app.repositories.job_repo import JobRepository
from app.repositories.resume_repo import ResumeRepository


logger = logging.getLogger(__name__)


class JobRecommendationService:
    """
    Service layer for AI Job Recommendation Engine.
    """

    def __init__(self, db) -> None:
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.recommendation_repo = JobRecommendationRepository(db)

    def generate_recommendations(
        self,
        user_id: int,
        resume_id: int,
        target_role: str | None = None,
        provider: str | None = None,
        model_name: str | None = None,
        top_n: int = 5
    ) -> Dict[str, Any]:
        resume = self.resume_repo.get_resume_by_id(
            resume_id=resume_id,
            user_id=user_id
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        resume_text = (resume.extracted_text or "").strip()

        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume does not contain extracted text"
            )

        jobs = self.job_repo.get_user_jobs(
            user_id=user_id,
            skip=0,
            limit=100
        )

        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No job descriptions found for recommendation"
            )

        resume_skills = set(
            extract_skills(resume_text)
        )

        recommendations = []

        for job in jobs:
            job_text = (
                (job.description or "")
                + " "
                + (job.required_skills or "")
            )

            job_skills = set(
                extract_skills(job_text)
            )

            matched_skills = sorted(
                list(resume_skills.intersection(job_skills))
            )

            missing_skills = sorted(
                list(job_skills.difference(resume_skills))
            )

            if len(job_skills) == 0:
                match_score = 0
            else:
                match_score = int(
                    (len(matched_skills) / len(job_skills)) * 100
                )

            if target_role:
                role_text = target_role.lower()
                title_text = (job.title or "").lower()

                if role_text in title_text:
                    match_score = min(match_score + 10, 100)

            recommendations.append(
                {
                    "job_id": job.id,
                    "title": job.title,
                    "company_name": job.company_name,
                    "match_score": match_score,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills
                }
            )

        recommendations = sorted(
            recommendations,
            key=lambda item: item["match_score"],
            reverse=True
        )[:top_n]

        all_missing_skills = []

        for item in recommendations:
            all_missing_skills.extend(item["missing_skills"])

        unique_missing_skills = sorted(
            list(set(all_missing_skills))
        )

        final_provider = provider or settings.LLM_PROVIDER
        final_model_name = model_name or settings.LLM_MODEL

        llm_client = LLMClient(
            provider=final_provider,
            model_name=final_model_name
        )

        recommendation_summary = (
            llm_client.generate_job_recommendation_summary(
                resume_text=resume_text,
                target_role=target_role,
                recommended_jobs=recommendations
            )
        )

        report_data = {
            "user_id": user_id,
            "resume_id": resume.id,
            "target_role": target_role,
            "resume_skills": ", ".join(sorted(list(resume_skills))),
            "recommended_jobs": json.dumps(recommendations),
            "missing_skills_summary": ", ".join(unique_missing_skills),
            "recommendation_summary": recommendation_summary,
            "provider": final_provider,
            "model_name": final_model_name
        }

        report = self.recommendation_repo.create_report(
            report_data
        )

        logger.info(
            "Job recommendations generated | user_id=%s report_id=%s",
            user_id,
            report.id
        )

        return self._serialize_report(report)

    def get_report(
        self,
        report_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        report = self.recommendation_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job recommendation report not found"
            )

        return self._serialize_report(report)

    def get_my_reports(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        reports = self.recommendation_repo.get_reports_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

        return [
            self._serialize_report(report)
            for report in reports
        ]

    def search_reports(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        cleaned_search = search.strip()

        if not cleaned_search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )

        reports = self.recommendation_repo.search_reports(
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
        report = self.recommendation_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job recommendation report not found"
            )

        updated_report = self.recommendation_repo.update_report(
            report=report,
            update_data=update_data
        )

        return self._serialize_report(updated_report)

    def delete_report(
        self,
        report_id: int,
        user_id: int
    ) -> Dict[str, str]:
        report = self.recommendation_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job recommendation report not found"
            )

        self.recommendation_repo.delete_report(report)

        return {
            "message": "Job recommendation report deleted successfully"
        }

    def batch_delete_reports(
        self,
        user_id: int,
        report_ids: List[int]
    ) -> Dict[str, Any]:
        if not report_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report_ids cannot be empty"
            )

        deleted_count = self.recommendation_repo.batch_delete_reports(
            user_id=user_id,
            report_ids=report_ids
        )

        return {
            "deleted_count": deleted_count,
            "message": f"{deleted_count} job recommendation report(s) deleted successfully"
        }

    def _serialize_report(
        self,
        report
    ) -> Dict[str, Any]:
        return {
            "id": report.id,
            "user_id": report.user_id,
            "resume_id": report.resume_id,
            "target_role": report.target_role,
            "resume_skills": report.resume_skills,
            "recommended_jobs": self._json_to_recommendations(
                report.recommended_jobs
            ),
            "missing_skills_summary": report.missing_skills_summary,
            "recommendation_summary": report.recommendation_summary,
            "provider": report.provider,
            "model_name": report.model_name,
            "created_at": report.created_at,
            "updated_at": report.updated_at
        }

    def _json_to_recommendations(
        self,
        value: str | None
    ) -> List[Dict[str, Any]]:
        if not value:
            return []

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

            return []

        except Exception:
            logger.exception("Failed to parse job recommendations JSON.")
            return []