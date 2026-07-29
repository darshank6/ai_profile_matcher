from typing import List

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.ats import ATSReportResponse
from app.schemas.ats import ATSResponse
from app.services.ats_service import ATSService


router = APIRouter()


@router.get(
    "/score/{resume_id}/{job_id}",
    response_model=ATSResponse
)
def generate_ats_score_endpoint(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = ATSService(db)

    return service.generate_ats_score(
        user_id=current_user.id,
        resume_id=resume_id,
        job_id=job_id
    )


@router.get(
    "/reports",
    response_model=List[ATSReportResponse]
)
def list_ats_reports_endpoint(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = ATSService(db)

    return service.get_my_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/reports/{report_id}",
    response_model=ATSReportResponse
)
def get_ats_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = ATSService(db)

    return service.get_report(
        report_id=report_id,
        user_id=current_user.id
    )


@router.delete(
    "/reports/{report_id}"
)
def delete_ats_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = ATSService(db)

    return service.delete_report(
        report_id=report_id,
        user_id=current_user.id
    )