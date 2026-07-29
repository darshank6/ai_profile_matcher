from typing import List

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies import (
    get_current_user
)

from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse
)

from app.services.job_service import (
    JobService
)

router = APIRouter()

@router.post(
    "/",
    response_model=JobResponse
)
def create_job(
    request: JobCreate,
    db: Session = Depends(
        get_db
    ),
    current_user=Depends(
        get_current_user
    )
):

    service = JobService(db)

    return service.create_job(
        current_user.id,
        request
    )

@router.get(
    "/",
    response_model=List[JobResponse]
)
def get_jobs(
    db: Session = Depends(
        get_db
    ),
    current_user=Depends(
        get_current_user
    )
):

    service = JobService(db)

    return service.get_jobs(
        current_user.id
    )

@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(
        get_db
    ),
    current_user=Depends(
        get_current_user
    )
):

    service = JobService(db)

    return service.get_job(
        job_id,
        current_user.id
    )


# @router.get(
#     "/{job_id}",
#     response_model=JobResponse
# )
# def get_job(
#     job_id: int,
#     db: Session = Depends(
#         get_db
#     ),
#     current_user=Depends(
#         get_current_user
#     )
# ):

#     service = JobService(db)

#     return service.get_job(
#         job_id,
#         current_user.id
#     )


@router.delete(
    "/{job_id}"
)
def delete_job(
    job_id: int,
    db: Session = Depends(
        get_db
    ),
    current_user=Depends(
        get_current_user
    )
):

    service = JobService(db)

    return service.delete_job(
        job_id,
        current_user.id
    )