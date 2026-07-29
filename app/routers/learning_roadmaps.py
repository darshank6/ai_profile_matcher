from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

from app.schemas.learning_roadmap import (
    LearningRoadmapBatchDeleteRequest,
)
from app.schemas.learning_roadmap import (
    LearningRoadmapBatchDeleteResponse,
)
from app.schemas.learning_roadmap import (
    LearningRoadmapDeleteResponse,
)
from app.schemas.learning_roadmap import (
    LearningRoadmapGenerateRequest,
)
from app.schemas.learning_roadmap import (
    LearningRoadmapResponse,
)
from app.schemas.learning_roadmap import (
    LearningRoadmapUpdateRequest,
)

from app.services.learning_roadmap_service import (
    LearningRoadmapService,
)

router = APIRouter()


@router.post(
    "/generate",
    response_model=LearningRoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI Learning Roadmap",
)
def generate_learning_roadmap(
    request: LearningRoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate personalized learning roadmap
    using resume + target role.
    """

    service = LearningRoadmapService(db)

    return service.generate_learning_roadmap(
        user_id=current_user.id,
        resume_id=request.resume_id,
        target_role=request.target_role,
        provider=request.provider,
        model_name=request.model_name,
    )


@router.get(
    "/",
    response_model=List[LearningRoadmapResponse],
    summary="Get My Learning Roadmaps",
)
def list_learning_roadmaps(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return paginated roadmaps
    for currently authenticated user.
    """

    service = LearningRoadmapService(db)

    return service.get_my_roadmaps(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/search",
    response_model=List[LearningRoadmapResponse],
    summary="Search Learning Roadmaps",
)
def search_learning_roadmaps(
    query: str = Query(
        ...,
        min_length=1,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Search roadmap reports.
    """

    service = LearningRoadmapService(db)

    return service.search_roadmaps(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/target-role/{target_role}",
    response_model=List[LearningRoadmapResponse],
    summary="Filter Roadmaps By Target Role",
)
def get_roadmaps_by_target_role(
    target_role: str,
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Filter learning roadmaps by target role.
    """

    service = LearningRoadmapService(db)

    return service.get_roadmaps_by_target_role(
        user_id=current_user.id,
        target_role=target_role,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{roadmap_id}",
    response_model=LearningRoadmapResponse,
    summary="Get Learning Roadmap",
)
def get_learning_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get one roadmap by ID.
    """

    service = LearningRoadmapService(db)

    return service.get_roadmap(
        roadmap_id=roadmap_id,
        user_id=current_user.id,
    )


@router.put(
    "/{roadmap_id}",
    response_model=LearningRoadmapResponse,
    summary="Update Learning Roadmap",
)
def update_learning_roadmap(
    roadmap_id: int,
    request: LearningRoadmapUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update roadmap metadata.
    """

    service = LearningRoadmapService(db)

    return service.update_roadmap(
        roadmap_id=roadmap_id,
        user_id=current_user.id,
        update_data=request.model_dump(),
    )


@router.delete(
    "/{roadmap_id}",
    response_model=LearningRoadmapDeleteResponse,
    summary="Delete Learning Roadmap",
)
def delete_learning_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete one roadmap report.
    """

    service = LearningRoadmapService(db)

    return service.delete_roadmap(
        roadmap_id=roadmap_id,
        user_id=current_user.id,
    )


@router.post(
    "/batch-delete",
    response_model=LearningRoadmapBatchDeleteResponse,
    summary="Batch Delete Learning Roadmaps",
)
def batch_delete_learning_roadmaps(
    request: LearningRoadmapBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete multiple roadmap reports.
    """

    service = LearningRoadmapService(db)

    return service.batch_delete_roadmaps(
        user_id=current_user.id,
        roadmap_ids=request.roadmap_ids,
    )