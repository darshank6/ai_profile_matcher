from fastapi import HTTPException

from app.repositories.job_repo import (
    JobRepository
)


class JobService:

    def __init__(self, db):

        self.repo = JobRepository(db)

    def create_job(
        self,
        user_id,
        request
    ):

        job_data = request.model_dump()

        job_data["user_id"] = user_id

        return self.repo.create_job(
            job_data
        )

    def get_jobs(
        self,
        user_id
    ):
        return self.repo.get_user_jobs(
            user_id
        )

    def get_job(
        self,
        job_id,
        user_id
    ):

        job = self.repo.get_job_by_id(
            job_id,
            user_id
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return job

    def update_job(
        self,
        job_id,
        user_id,
        request
    ):

        job = self.repo.get_job_by_id(
            job_id,
            user_id
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return self.repo.update_job(
            job,
            request.model_dump()
        )

    def delete_job(
        self,
        job_id,
        user_id
    ):

        job = self.repo.get_job_by_id(
            job_id,
            user_id
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        self.repo.delete_job(job)

        return {
            "message":
            "Job deleted successfully"
        }