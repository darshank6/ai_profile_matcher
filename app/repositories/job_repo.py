from typing import List
from typing import Optional

from sqlalchemy.orm import Session

from app.models.job import JobDescription


class JobRepository:
    """
    Repository for JobDescription database operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_job(
        self,
        job_data: dict
    ) -> JobDescription:
        job = JobDescription(**job_data)

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_job_by_id(
        self,
        job_id: int,
        user_id: int
    ) -> Optional[JobDescription]:
        return (
            self.db.query(JobDescription)
            .filter(JobDescription.id == job_id)
            .filter(JobDescription.user_id == user_id)
            .first()
        )

    def get_user_jobs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobDescription]:
        return (
            self.db.query(JobDescription)
            .filter(JobDescription.user_id == user_id)
            .order_by(JobDescription.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_job(
        self,
        job: JobDescription,
        update_data: dict
    ) -> JobDescription:
        for key, value in update_data.items():
            if value is not None:
                setattr(job, key, value)

        self.db.commit()
        self.db.refresh(job)

        return job

    def delete_job(
        self,
        job: JobDescription
    ) -> bool:
        self.db.delete(job)
        self.db.commit()

        return True

# from sqlalchemy.orm import Session

# from app.models.job import JobDescription


# class JobRepository:

#     def __init__(
#         self,
#         db: Session
#     ):
#         self.db = db

#     def create_job(
#         self,
#         job_data: dict
#     ):

#         job = JobDescription(
#             **job_data
#         )

#         self.db.add(job)

#         self.db.commit()

#         self.db.refresh(job)

#         return job

#     def get_job_by_id(
#         self,
#         job_id: int,
#         user_id: int
#     ):

#         return (
#             self.db.query(
#                 JobDescription
#             )
#             .filter(
#                 JobDescription.id == job_id
#             )
#             .filter(
#                 JobDescription.user_id == user_id
#             )
#             .first()
#         )

#     def get_user_jobs(
#         self,
#         user_id: int
#     ):

#         return (
#             self.db.query(
#                 JobDescription
#             )
#             .filter(
#                 JobDescription.user_id == user_id
#             )
#             .all()
#         )

#     def update_job(
#         self,
#         job,
#         update_data
#     ):

#         for key, value in update_data.items():

#             if value is not None:

#                 setattr(
#                     job,
#                     key,
#                     value
#                 )

#         self.db.commit()

#         self.db.refresh(job)

#         return job

#     def delete_job(
#         self,
#         job
#     ):
#         self.db.delete(job)

#         self.db.commit()