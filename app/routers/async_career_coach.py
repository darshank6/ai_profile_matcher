from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.career_coach import CareerCoachAskRequest
from app.schemas.career_coach import CareerCoachAskResponse
from app.schemas.career_coach import CareerCoachMessageResponse
from app.schemas.career_coach import CareerCoachSessionCreateRequest
from app.schemas.career_coach import CareerCoachSessionResponse
from app.services.async_career_coach_service import AsyncCareerCoachService


router = APIRouter()


@router.post(
    "/sessions",
    response_model=CareerCoachSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create async career coach session",
)
async def create_async_career_coach_session(
    request: CareerCoachSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AsyncCareerCoachService(db)

    return await service.create_session(
        user_id=current_user.id,
        title=request.title,
        target_role=request.target_role,
    )


@router.get(
    "/sessions",
    response_model=list[CareerCoachSessionResponse],
    summary="List async career coach sessions",
)
async def list_async_career_coach_sessions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AsyncCareerCoachService(db)

    return await service.get_my_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/sessions/search",
    response_model=list[CareerCoachSessionResponse],
    summary="Search async career coach sessions",
)
async def search_async_career_coach_sessions(
    query: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AsyncCareerCoachService(db)

    return await service.search_sessions(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/ask",
    response_model=CareerCoachAskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ask async AI career coach",
)
async def ask_async_career_coach(
    request: CareerCoachAskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AsyncCareerCoachService(db)

    return await service.ask_question(
        user_id=current_user.id,
        question=request.question,
        session_id=request.session_id,
        target_role=request.target_role,
        top_k=request.top_k,
        provider=request.provider,
        model_name=request.model_name,
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[CareerCoachMessageResponse],
    summary="Get async career coach session messages",
)
async def get_async_career_coach_messages(
    session_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AsyncCareerCoachService(db)

    return await service.get_session_messages(
        user_id=current_user.id,
        session_id=session_id,
        skip=skip,
        limit=limit,
    )