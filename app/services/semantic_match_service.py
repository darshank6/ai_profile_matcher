import json
import logging
from typing import Any
from typing import Dict
from typing import List

from fastapi import HTTPException
from fastapi import status

from app.ai.semantic_matcher import SemanticMatcher
from app.ai.skill_extractor import extract_skills
from app.repositories.job_repo import JobRepository
from app.repositories.resume_repo import ResumeRepository
from app.repositories.semantic_match_repo import SemanticMatchRepository


logger = logging.getLogger(__name__)


class SemanticMatchService:
    """
    Service layer for semantic ATS matching.

    Responsibilities:
    - Validate resume ownership
    - Validate job ownership
    - Extract resume/job skills
    - Compute keyword score
    - Compute semantic similarity score
    - Compute overall weighted score
    - Save semantic report
    - Serialize database model into API response
    """

    def __init__(
        self,
        db,
    ) -> None:
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.semantic_repo = SemanticMatchRepository(db)
        self.matcher = SemanticMatcher()

    def generate_semantic_match(
        self,
        user_id: int,
        resume_id: int,
        job_id: int,
    ) -> Dict[str, Any]:
        """
        Generate a new semantic ATS matching report.
        """

        resume = self.resume_repo.get_resume_by_id(
            resume_id=resume_id,
            user_id=user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        job = self.job_repo.get_job_by_id(
            job_id=job_id,
            user_id=user_id,
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found",
            )

        resume_text = (resume.extracted_text or "").strip()

        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume does not contain extracted text",
            )

        job_text = (
            f"{job.title or ''} "
            f"{job.description or ''} "
            f"{job.required_skills or ''}"
        ).strip()

        if not job_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is empty",
            )

        resume_skills = set(extract_skills(resume_text))
        job_skills = set(extract_skills(job_text))

        matched_skills = sorted(
            list(resume_skills.intersection(job_skills))
        )

        missing_skills = sorted(
            list(job_skills.difference(resume_skills))
        )

        keyword_score = self.matcher.keyword_score(
            resume_skills=resume_skills,
            job_skills=job_skills,
        )

        semantic_score = self.matcher.semantic_score(
            resume_text=resume_text,
            job_text=job_text,
        )

        overall_score = self.matcher.overall_score(
            keyword_score=keyword_score,
            semantic_score=semantic_score,
        )

        match_explanation = self.matcher.build_explanation(
            overall_score=overall_score,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        )

        recommendation = self.matcher.build_recommendation(
            overall_score=overall_score,
            missing_skills=missing_skills,
        )

        report_data = {
            "user_id": user_id,
            "resume_id": resume.id,
            "job_id": job.id,
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "overall_score": overall_score,
            "resume_skills": json.dumps(
                sorted(list(resume_skills)),
                ensure_ascii=False,
            ),
            "job_skills": json.dumps(
                sorted(list(job_skills)),
                ensure_ascii=False,
            ),
            "matched_skills": json.dumps(
                matched_skills,
                ensure_ascii=False,
            ),
            "missing_skills": json.dumps(
                missing_skills,
                ensure_ascii=False,
            ),
            "match_explanation": match_explanation,
            "recommendation": recommendation,
            "provider": "local",
            "model_name": "token-cosine-semantic-v1",
        }

        report = self.semantic_repo.create_report(report_data)

        logger.info(
            "Semantic match generated | user_id=%s resume_id=%s job_id=%s report_id=%s",
            user_id,
            resume_id,
            job_id,
            report.id,
        )

        return self._serialize_report(report)

    def get_report(
        self,
        report_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Get one semantic match report.
        """

        report = self.semantic_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id,
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semantic match report not found",
            )

        return self._serialize_report(report)

    def get_my_reports(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get paginated semantic reports for current user.
        """

        reports = self.semantic_repo.get_reports_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
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
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search semantic reports.
        """

        cleaned_search = search.strip()

        if not cleaned_search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty",
            )

        reports = self.semantic_repo.search_reports(
            user_id=user_id,
            search=cleaned_search,
            skip=skip,
            limit=limit,
        )

        return [
            self._serialize_report(report)
            for report in reports
        ]

    def update_report(
        self,
        report_id: int,
        user_id: int,
        update_data: dict,
    ) -> Dict[str, Any]:
        """
        Update editable fields in a semantic report.
        """

        report = self.semantic_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id,
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semantic match report not found",
            )

        updated_report = self.semantic_repo.update_report(
            report=report,
            update_data=update_data,
        )

        logger.info(
            "Semantic match report updated | user_id=%s report_id=%s",
            user_id,
            report_id,
        )

        return self._serialize_report(updated_report)

    def delete_report(
        self,
        report_id: int,
        user_id: int,
    ) -> Dict[str, str]:
        """
        Delete one semantic report.
        """

        report = self.semantic_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id,
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semantic match report not found",
            )

        self.semantic_repo.delete_report(report)

        logger.info(
            "Semantic match report deleted | user_id=%s report_id=%s",
            user_id,
            report_id,
        )

        return {
            "message": "Semantic match report deleted successfully"
        }

    def batch_delete_reports(
        self,
        user_id: int,
        report_ids: List[int],
    ) -> Dict[str, Any]:
        """
        Batch delete semantic reports.
        """

        if not report_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report_ids cannot be empty",
            )

        deleted_count = self.semantic_repo.batch_delete_reports(
            user_id=user_id,
            report_ids=report_ids,
        )

        logger.info(
            "Batch deleted semantic reports | user_id=%s deleted_count=%s",
            user_id,
            deleted_count,
        )

        return {
            "deleted_count": deleted_count,
            "message": f"{deleted_count} semantic match report(s) deleted successfully",
        }

    def _serialize_report(
        self,
        report,
    ) -> Dict[str, Any]:
        """
        Convert SQLAlchemy object into API response dict.
        """

        return {
            "id": report.id,
            "user_id": report.user_id,
            "resume_id": report.resume_id,
            "job_id": report.job_id,
            "keyword_score": report.keyword_score,
            "semantic_score": report.semantic_score,
            "overall_score": report.overall_score,
            "resume_skills": self._json_to_list(report.resume_skills),
            "job_skills": self._json_to_list(report.job_skills),
            "matched_skills": self._json_to_list(report.matched_skills),
            "missing_skills": self._json_to_list(report.missing_skills),
            "match_explanation": report.match_explanation,
            "recommendation": report.recommendation,
            "provider": report.provider,
            "model_name": report.model_name,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
        }

    def _json_to_list(
        self,
        value: str | None,
    ) -> List[str]:
        """
        Convert stored JSON string into Python list of strings.
        """

        if not value:
            return []

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return [str(item) for item in parsed]

            if isinstance(parsed, str):
                return [parsed]

            return []

        except Exception:
            logger.exception("Failed to parse semantic match JSON field.")
            return []