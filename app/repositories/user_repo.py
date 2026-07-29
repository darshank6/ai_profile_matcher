from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):

        self.db = db

    def create_user(self, user_data):

        user = User(**user_data)

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user

    def get_by_email(self, email):

        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_id(self, user_id):

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )