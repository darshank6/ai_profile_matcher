from fastapi import HTTPException
from fastapi import status

from app.repositories.user_repo import UserRepository

from app.utils.security import create_access_token
from app.utils.security import hash_password
from app.utils.security import verify_password


class AuthService:

    def __init__(self, db):
        self.db = db

    def login(
        self,
        email: str,
        password: str
    ):
        user = UserRepository(
            self.db
        ).get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not verify_password(
            password,
            user.password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        token = create_access_token(
            {"sub": str(user.id)}
        )

        return token



    def register(self, request):
        existing_user = self.user_repo.get_by_email(
            request.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = hash_password(
            request.password
        )

        user_data = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "role": request.role
        }

        user = self.user_repo.create_user(
            user_data
        )

        return user

    # def login(self, request):
    #     user = self.user_repo.get_by_email(
    #         request.email
    #     )

    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid email or password"
    #         )

    #     is_password_valid = verify_password(
    #         request.password,
    #         user.password
    #     )

    #     if not is_password_valid:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid email or password"
    #         )

    #     token_data = {
    #         "sub": str(user.id),
    #         "email": user.email,
    #         "role": user.role
    #     }

    #     access_token = create_access_token(
    #         token_data
    #     )

    #     return {
    #         "access_token": access_token,
    #         "token_type": "bearer"
    #     }