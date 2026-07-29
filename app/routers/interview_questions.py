from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.interview_question import InterviewQuestionBatchDeleteRequest
from app.schemas.interview_question import InterviewQuestionBatchDeleteResponse
from app.schemas.interview_question import InterviewQuestionDeleteResponse
from app.schemas.interview_question import InterviewQuestionGenerateRequest
from app.schemas.interview_question import InterviewQuestionReportResponse
from app.schemas.interview_question import InterviewQuestionUpdateRequest
from app.services.interview_question_service import InterviewQuestionService


router = APIRouter()


@router.post(
    "/generate",
    response_model=InterviewQuestionReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI interview questions"
)
def generate_interview_questions_endpoint(
    request: InterviewQuestionGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.generate_interview_questions(
        user_id=current_user.id,
        resume_id=request.resume_id,
        job_id=request.job_id,
        provider=request.provider,
        model_name=request.model_name
    )


@router.get(
    "/",
    response_model=List[InterviewQuestionReportResponse],
    summary="List my interview question reports"
)
def list_interview_question_reports_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.get_my_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/search",
    response_model=List[InterviewQuestionReportResponse],
    summary="Search interview question reports"
)
def search_interview_question_reports_endpoint(
    query: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.search_reports(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{report_id}",
    response_model=InterviewQuestionReportResponse,
    summary="Get one interview question report"
)
def get_interview_question_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.get_report(
        report_id=report_id,
        user_id=current_user.id
    )


@router.put(
    "/{report_id}",
    response_model=InterviewQuestionReportResponse,
    summary="Update interview question report"
)
def update_interview_question_report_endpoint(
    report_id: int,
    request: InterviewQuestionUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.update_report(
        report_id=report_id,
        user_id=current_user.id,
        update_data=request.model_dump()
    )


@router.delete(
    "/{report_id}",
    response_model=InterviewQuestionDeleteResponse,
    summary="Delete interview question report"
)
def delete_interview_question_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.delete_report(
        report_id=report_id,
        user_id=current_user.id
    )


@router.post(
    "/batch-delete",
    response_model=InterviewQuestionBatchDeleteResponse,
    summary="Batch delete interview question reports"
)
def batch_delete_interview_question_reports_endpoint(
    request: InterviewQuestionBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = InterviewQuestionService(db)

    return service.batch_delete_reports(
        user_id=current_user.id,
        report_ids=request.report_ids
    )