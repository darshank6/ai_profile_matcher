from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.semantic_match import SemanticMatchBatchDeleteRequest
from app.schemas.semantic_match import SemanticMatchBatchDeleteResponse
from app.schemas.semantic_match import SemanticMatchDeleteResponse
from app.schemas.semantic_match import SemanticMatchGenerateRequest
from app.schemas.semantic_match import SemanticMatchResponse
from app.schemas.semantic_match import SemanticMatchUpdateRequest
from app.services.semantic_match_service import SemanticMatchService


router = APIRouter()


@router.post(
    "/generate",
    response_model=SemanticMatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate semantic ATS match",
)
def generate_semantic_match_endpoint(
    request: SemanticMatchGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate semantic ATS match using resume and job description.
    """

    service = SemanticMatchService(db)

    return service.generate_semantic_match(
        user_id=current_user.id,
        resume_id=request.resume_id,
        job_id=request.job_id,
    )


@router.get(
    "/",
    response_model=List[SemanticMatchResponse],
    summary="List semantic match reports",
)
def list_semantic_match_reports_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List semantic reports for authenticated user.
    """

    service = SemanticMatchService(db)

    return service.get_my_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/search",
    response_model=List[SemanticMatchResponse],
    summary="Search semantic match reports",
)
def search_semantic_match_reports_endpoint(
    query: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Search semantic reports.
    """

    service = SemanticMatchService(db)

    return service.search_reports(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{report_id}",
    response_model=SemanticMatchResponse,
    summary="Get semantic match report by ID",
)
def get_semantic_match_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get one semantic report.
    """

    service = SemanticMatchService(db)

    return service.get_report(
        report_id=report_id,
        user_id=current_user.id,
    )


@router.put(
    "/{report_id}",
    response_model=SemanticMatchResponse,
    summary="Update semantic match report",
)
def update_semantic_match_report_endpoint(
    report_id: int,
    request: SemanticMatchUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update editable semantic report fields.
    """

    service = SemanticMatchService(db)

    return service.update_report(
        report_id=report_id,
        user_id=current_user.id,
        update_data=request.model_dump(),
    )


@router.delete(
    "/{report_id}",
    response_model=SemanticMatchDeleteResponse,
    summary="Delete semantic match report",
)
def delete_semantic_match_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete one semantic report.
    """

    service = SemanticMatchService(db)

    return service.delete_report(
        report_id=report_id,
        user_id=current_user.id,
    )


@router.post(
    "/batch-delete",
    response_model=SemanticMatchBatchDeleteResponse,
    summary="Batch delete semantic match reports",
)
def batch_delete_semantic_match_reports_endpoint(
    request: SemanticMatchBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Batch delete semantic reports.
    """

    service = SemanticMatchService(db)

    return service.batch_delete_reports(
        user_id=current_user.id,
        report_ids=request.report_ids,
    )