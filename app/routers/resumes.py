from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import UploadFile

from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

from app.schemas.resume import ResumeListResponse
from app.schemas.resume import ResumeResponse

from app.services.resume_service import ResumeService


router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeResponse
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    resume_service = ResumeService(db)

    resume = await resume_service.upload_resume(
        user_id=current_user.id,
        file=file
    )

    return resume


@router.get(
    "/",
    response_model=List[ResumeListResponse]
)
def get_my_resumes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    resume_service = ResumeService(db)

    resumes = resume_service.get_my_resumes(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return resumes


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse
)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    resume_service = ResumeService(db)

    resume = resume_service.get_resume(
        resume_id=resume_id,
        user_id=current_user.id
    )

    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    resume_service = ResumeService(db)

    result = resume_service.delete_resume(
        resume_id=resume_id,
        user_id=current_user.id
    )

    return result