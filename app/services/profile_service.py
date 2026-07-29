from fastapi import HTTPException
from fastapi import status

from app.repositories.profile_repo import (
    ProfileRepository
)

class ProfileService:

    def __init__(
        self,
        db
    ):

        self.repo = ProfileRepository(
            db
        )

    
    def create_profile(
        self,
        user_id,
        request
    ):

        existing_profile = self.repo.get_by_user_id(
            user_id
        )

        if existing_profile:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Profile already exists"

            )

        return self.repo.create_profile(

            user_id,

            request.model_dump()

        )

    def get_profile(
        self,
        user_id
    ):

        profile = self.repo.get_by_user_id(
            user_id
        )

        if not profile:

            raise HTTPException(

                status_code=404,

                detail="Profile not found"
            )

        return profile


    def update_profile(
        self,
        user_id,
        request
    ):

        profile = self.repo.get_by_user_id(
            user_id
        )

        if not profile:

            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        return self.repo.update_profile(

            profile,

            request.model_dump()

        )


    def delete_profile(
        self,
        user_id
    ):

        profile = self.repo.get_by_user_id(
            user_id
        )

        if not profile:

            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        self.repo.delete_profile(profile)

        return {
            "message": "Profile deleted"
        }