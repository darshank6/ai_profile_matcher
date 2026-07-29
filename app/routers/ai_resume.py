from typing import List

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.ai_resume import AIResumeAnalyzeRequest
from app.schemas.ai_resume import AIResumeReportResponse
from app.services.ai_resume_service import AIResumeService


router = APIRouter()


@router.post(
    "/resumes/{resume_id}/analyze",
    response_model=AIResumeReportResponse
)
def analyze_resume_endpoint(
    resume_id: int,
    request: AIResumeAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = AIResumeService(db)

    return service.analyze_resume(
        user_id=current_user.id,
        resume_id=resume_id,
        provider=request.provider,
        model_name=request.model_name
    )


@router.get(
    "/resumes/reports",
    response_model=List[AIResumeReportResponse]
)
def list_ai_resume_reports_endpoint(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = AIResumeService(db)

    return service.get_my_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/resumes/reports/{report_id}",
    response_model=AIResumeReportResponse
)
def get_ai_resume_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = AIResumeService(db)

    return service.get_report(
        report_id=report_id,
        user_id=current_user.id
    )


@router.delete(
    "/resumes/reports/{report_id}"
)
def delete_ai_resume_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = AIResumeService(db)

    return service.delete_report(
        report_id=report_id,
        user_id=current_user.id
    )