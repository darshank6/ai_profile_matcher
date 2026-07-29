from sqlalchemy.orm import Session

from app.models.profile import UserProfile


class ProfileRepository:

    def __init__(self, db: Session):

        self.db = db

    def create_profile(
        self,
        user_id,
        profile_data
    ):

        profile = UserProfile(

            user_id=user_id,

            **profile_data

        )

        self.db.add(profile)

        self.db.commit()

        self.db.refresh(profile)

        return profile


    def get_by_user_id(
        self,
        user_id
    ):

        return (

            self.db.query(UserProfile)

            .filter(
                UserProfile.user_id == user_id
            )

            .first()

        )

    def delete_profile(
        self,
        profile
    ):

        self.db.delete(profile)

        self.db.commit()
        


    def update_profile(
        self,
        profile,
        data
    ):

        for key, value in data.items():

            if value is not None:

                setattr(
                    profile,
                    key,
                    value
                )

        self.db.commit()

        self.db.refresh(profile)

        return profile