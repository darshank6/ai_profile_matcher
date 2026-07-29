from fastapi import HTTPException
from fastapi import status

from app.ai.skill_extractor import extract_skills
from app.repositories.ats_repo import ATSRepository
from app.repositories.job_repo import JobRepository
from app.repositories.resume_repo import ResumeRepository


class ATSService:
    def __init__(self, db):
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.ats_repo = ATSRepository(db)

    def generate_ats_score(
        self,
        user_id: int,
        resume_id: int,
        job_id: int
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

        job = self.job_repo.get_job_by_id(
            job_id=job_id,
            user_id=user_id
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        resume_text = resume.extracted_text or ""
        job_text = job.description or ""

        resume_skills = set(extract_skills(resume_text))
        job_skills = set(extract_skills(job_text))

        matched_skills = sorted(
            list(resume_skills.intersection(job_skills))
        )

        missing_skills = sorted(
            list(job_skills.difference(resume_skills))
        )

        if len(job_skills) == 0:
            ats_score = 0
        else:
            ats_score = int(
                (len(matched_skills) / len(job_skills)) * 100
            )

        strengths = []

        if ats_score >= 80:
            strengths.append(
                "Strong alignment with the job description"
            )

        if "python" in matched_skills:
            strengths.append(
                "Strong Python backend profile"
            )

        if "fastapi" in matched_skills:
            strengths.append(
                "Relevant FastAPI backend development experience"
            )

        if "postgresql" in matched_skills:
            strengths.append(
                "Good relational database experience"
            )

        if not strengths:
            strengths.append(
                "Some relevant skills found, but profile needs improvement"
            )

        recommendations = []

        for skill in missing_skills:
            recommendations.append(
                f"Learn and add practical experience in {skill}"
            )

        if not recommendations:
            recommendations.append(
                "Your resume skills strongly match this job description"
            )

        report_data = {
            "user_id": user_id,
            "resume_id": resume.id,
            "job_id": job.id,
            "candidate_name": None,
            "candidate_email": None,
            "resume_text": resume_text,
            "job_description_text": job_text,
            "extracted_resume_skills": ", ".join(
                sorted(list(resume_skills))
            ),
            "extracted_job_skills": ", ".join(
                sorted(list(job_skills))
            ),
            "matched_skills": ", ".join(matched_skills),
            "missing_skills": ", ".join(missing_skills),
            "strengths": " | ".join(strengths),
            "recommendations": " | ".join(recommendations),
            "match_score": float(ats_score)
        }

        report = self.ats_repo.create_report(report_data)

        return {
            "report_id": report.id,
            "ats_score": ats_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "recommendations": recommendations
        }

    def get_my_reports(
        self,
        user_id: int,
        skip: int,
        limit: int
    ):
        return self.ats_repo.get_reports_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    def get_report(
        self,
        report_id: int,
        user_id: int
    ):
        report = self.ats_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ATS report not found"
            )

        return report

    def delete_report(
        self,
        report_id: int,
        user_id: int
    ):
        report = self.ats_repo.get_report_by_id(
            report_id=report_id,
            user_id=user_id
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ATS report not found"
            )

        self.ats_repo.delete_report(report)

        return {
            "message": "ATS report deleted successfully"
        }