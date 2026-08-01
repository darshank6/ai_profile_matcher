from typing import Optional

from django.contrib.postgres import search
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.career_coach import CareerCoachMessage
from app.models.career_coach import CareerCoachSession


class CareerCoachRepository:
    """
    Repository for career coach sessions and messages.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create_session(
        self,
        session_data: dict,
    ) -> CareerCoachSession:
        session = CareerCoachSession(
            **session_data
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_session_by_id(
        self,
        session_id: int,
        user_id: int,
    ) -> Optional[CareerCoachSession]:
        return (
            self.db.query(CareerCoachSession)
            .filter(CareerCoachSession.id == session_id)
            .filter(CareerCoachSession.user_id == user_id)
            .first()
        )

    def get_sessions_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> list[CareerCoachSession]:
        return (
            self.db.query(CareerCoachSession)
            .filter(CareerCoachSession.user_id == user_id)
            .order_by(CareerCoachSession.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_sessions(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10,
    ) -> list:
        search_pattern = f"%{search}%"

        return (
            self.db.query(CareerCoachSession)
            .filter(CareerCoachSession.user_id == user_id)
            .filter(
                or_(
                    CareerCoachSession.title.ilike(search_pattern),
                    CareerCoachSession.target_role.ilike(search_pattern),
                )
            )
            .order_by(CareerCoachSession.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_session(
        self,
        session: CareerCoachSession,
        update_data: dict,
    ) -> CareerCoachSession:
        for key, value in update_data.items():
            if value is not None:
                setattr(
                    session,
                    key,
                    value,
                )

        self.db.commit()
        self.db.refresh(session)

        return session

    def delete_session(
        self,
        session: CareerCoachSession,
    ) -> bool:
        self.db.delete(session)
        self.db.commit()

        return True

    def batch_delete_sessions(
        self,
        user_id: int,
        session_ids: list[int],
    ) -> int:
        sessions = (
            self.db.query(CareerCoachSession)
            .filter(CareerCoachSession.user_id == user_id)
            .filter(CareerCoachSession.id.in_(session_ids))
            .all()
        )

        deleted_count = len(sessions)

        for session in sessions:
            self.db.delete(session)

        self.db.commit()

        return deleted_count

    def create_message(
        self,
        message_data: dict,
    ) -> CareerCoachMessage:
        message = CareerCoachMessage(
            **message_data
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_messages_by_session(
        self,
        session_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CareerCoachMessage]:
        return (
            self.db.query(CareerCoachMessage)
            .filter(CareerCoachMessage.session_id == session_id)
            .filter(CareerCoachMessage.user_id == user_id)
            .order_by(CareerCoachMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_messages_by_session(
        self,
        session_id: int,
        user_id: int,
        limit: int = 8,
    ) -> list[CareerCoachMessage]:
        messages = (
            self.db.query(CareerCoachMessage)
            .filter(CareerCoachMessage.session_id == session_id)
            .filter(CareerCoachMessage.user_id == user_id)
            .order_by(CareerCoachMessage.created_at.desc())
            .limit(limit)
            .all()
        )

        return list(
            reversed(messages)
        )