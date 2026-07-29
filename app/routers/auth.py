from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies import get_current_user

from app.schemas.auth import LoginRequest
from app.schemas.auth import RegisterRequest
from app.schemas.auth import TokenResponse
from app.schemas.auth import UserResponse

from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    user = auth_service.register(
        request
    )

    return user
    


# This works with Login for swagger authorization
@router.post("/token")
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    token = auth_service.login(
        email=form_data.username,  # username = email
        password=form_data.password
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    token = auth_service.login(
        request.email,
        request.password
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
# @router.post(
#     "/login",
#     response_model=TokenResponse
# )
# def login(
#     request: LoginRequest,
#     db: Session = Depends(get_db)
# ):
#     auth_service = AuthService(db)

#     token = auth_service.login(
#         request
#     )

#     return token


@router.get(
    "/me",
    response_model=UserResponse
)
def get_logged_in_user(
    current_user=Depends(get_current_user)
):
    return current_user