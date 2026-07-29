from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.job_recommendation import JobRecommendationBatchDeleteRequest
from app.schemas.job_recommendation import JobRecommendationBatchDeleteResponse
from app.schemas.job_recommendation import JobRecommendationDeleteResponse
from app.schemas.job_recommendation import JobRecommendationGenerateRequest
from app.schemas.job_recommendation import JobRecommendationResponse
from app.schemas.job_recommendation import JobRecommendationUpdateRequest
from app.services.job_recommendation_service import JobRecommendationService


router = APIRouter()


@router.post(
    "/generate",
    response_model=JobRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate job recommendations"
)
def generate_job_recommendations_endpoint(
    request: JobRecommendationGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.generate_recommendations(
        user_id=current_user.id,
        resume_id=request.resume_id,
        target_role=request.target_role,
        provider=request.provider,
        model_name=request.model_name,
        top_n=request.top_n
    )


@router.get(
    "/",
    response_model=List[JobRecommendationResponse],
    summary="List job recommendation reports"
)
def list_job_recommendation_reports_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.get_my_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/search",
    response_model=List[JobRecommendationResponse],
    summary="Search job recommendation reports"
)
def search_job_recommendation_reports_endpoint(
    query: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.search_reports(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{report_id}",
    response_model=JobRecommendationResponse,
    summary="Get job recommendation report"
)
def get_job_recommendation_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.get_report(
        report_id=report_id,
        user_id=current_user.id
    )


@router.put(
    "/{report_id}",
    response_model=JobRecommendationResponse,
    summary="Update job recommendation report"
)
def update_job_recommendation_report_endpoint(
    report_id: int,
    request: JobRecommendationUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.update_report(
        report_id=report_id,
        user_id=current_user.id,
        update_data=request.model_dump()
    )


@router.delete(
    "/{report_id}",
    response_model=JobRecommendationDeleteResponse,
    summary="Delete job recommendation report"
)
def delete_job_recommendation_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.delete_report(
        report_id=report_id,
        user_id=current_user.id
    )


@router.post(
    "/batch-delete",
    response_model=JobRecommendationBatchDeleteResponse,
    summary="Batch delete job recommendation reports"
)
def batch_delete_job_recommendation_reports_endpoint(
    request: JobRecommendationBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = JobRecommendationService(db)

    return service.batch_delete_reports(
        user_id=current_user.id,
        report_ids=request.report_ids
    )