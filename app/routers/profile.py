from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies import get_current_user

from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse
)

from app.services.profile_service import (
    ProfileService
)

router = APIRouter()


@router.post(
    "/",
    response_model=ProfileResponse
)
def create_profile(
    request: ProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = ProfileService(db)

    return service.create_profile(
        current_user.id,
        request
    )


@router.get(
    "/me",
    response_model=ProfileResponse
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = ProfileService(db)

    return service.get_profile(
        current_user.id
    )


@router.put(
    "/me",
    response_model=ProfileResponse
)
def update_my_profile(
    request: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = ProfileService(db)

    return service.update_profile(
        current_user.id,
        request
    )


@router.delete("/me")
def delete_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    service = ProfileService(db)

    return service.delete_profile(
        current_user.id
    )