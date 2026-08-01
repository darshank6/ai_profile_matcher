import json
import logging
from typing import Any, Optional

from fastapi import HTTPException
from fastapi import status

from app.ai.async_rag_engine import AsyncRAGEngine
from app.ai.llm_client import LLMClient
from app.config import settings
from app.repositories.career_coach_repo import CareerCoachRepository
from app.repositories.rag_repo import RAGRepository
from app.utils.async_utils import run_blocking_io


logger = logging.getLogger(__name__)


class AsyncCareerCoachService:
    """
    Async service for AI Career Coach.

    Uses asyncio for:
    - async embedding generation
    - non-blocking RAG retrieval workflow
    - thread offloading for existing sync SQLAlchemy repositories
    """

    def __init__(
        self,
        db,
    ) -> None:
        self.career_repo = CareerCoachRepository(db)
        self.rag_repo = RAGRepository(db)
        self.rag_engine = AsyncRAGEngine()

    async def create_session(
        self,
        user_id: int,
        title: str,
        target_role: Optional[str] = None,
    ) -> dict[str, Any]:
        cleaned_title = title.strip()

        if not cleaned_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session title cannot be empty",
            )

        cleaned_target_role = (
            target_role.strip()
            if target_role
            else None
        )

        session = await run_blocking_io(
            self.career_repo.create_session,
            {
                "user_id": user_id,
                "title": cleaned_title,
                "target_role": cleaned_target_role,
                "is_active": True,
            },
        )

        return self._serialize_session(
            session
        )

    async def get_session(
        self,
        user_id: int,
        session_id: int,
    ) -> dict[str, Any]:
        session = await run_blocking_io(
            self.career_repo.get_session_by_id,
            session_id,
            user_id,
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Career coach session not found",
            )

        return self._serialize_session(
            session
        )

    async def get_my_sessions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        sessions = await run_blocking_io(
            self.career_repo.get_sessions_by_user,
            user_id,
            skip,
            limit,
        )

        return [
            self._serialize_session(session)
            for session in sessions
        ]

    async def search_sessions(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        cleaned_search = search.strip()

        if not cleaned_search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty",
            )

        sessions = await run_blocking_io(
            self.career_repo.search_sessions,
            user_id,
            cleaned_search,
            skip,
            limit,
        )

        return [
            self._serialize_session(session)
            for session in sessions
        ]

    async def ask_question(
        self,
        user_id: int,
        question: str,
        session_id: Optional[int] = None,
        target_role: Optional[str] = None,
        top_k: int = 5,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> dict[str, Any]:
        cleaned_question = question.strip()

        if not cleaned_question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty",
            )

        session = await self._get_or_create_session(
            user_id=user_id,
            session_id=session_id,
            question=cleaned_question,
            target_role=target_role,
        )

        final_provider = provider or settings.LLM_PROVIDER
        final_model_name = model_name or settings.LLM_MODEL

        user_message = await run_blocking_io(
            self.career_repo.create_message,
            {
                "user_id": user_id,
                "session_id": session.id,
                "role": "user",
                "content": cleaned_question,
                "context_chunks": None,
                "provider": final_provider,
                "model_name": final_model_name,
            },
        )

        recent_messages = await run_blocking_io(
            self.career_repo.get_recent_messages_by_session,
            session.id,
            user_id,
            8,
        )

        conversation_history = self._build_conversation_history(
            recent_messages
        )

        context_chunks = await self._retrieve_context_chunks(
            user_id=user_id,
            question=cleaned_question,
            top_k=top_k,
        )

        context_text = "\n\n".join(
            item["content"]
            for item in context_chunks
        )

        llm_client = LLMClient(
            provider=final_provider,
            model_name=final_model_name,
        )

        answer = await run_blocking_io(
            llm_client.generate_career_coach_answer,
            cleaned_question,
            context_text,
            conversation_history,
            session.target_role,
        )

        assistant_message = await run_blocking_io(
            self.career_repo.create_message,
            {
                "user_id": user_id,
                "session_id": session.id,
                "role": "assistant",
                "content": answer,
                "context_chunks": json.dumps(
                    context_chunks,
                    ensure_ascii=False,
                ),
                "provider": final_provider,
                "model_name": final_model_name,
            },
        )

        return {
            "session": self._serialize_session(session),
            "user_message": self._serialize_message(user_message),
            "assistant_message": self._serialize_message(assistant_message),
        }

    async def get_session_messages(
        self,
        user_id: int,
        session_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        session = await run_blocking_io(
            self.career_repo.get_session_by_id,
            session_id,
            user_id,
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Career coach session not found",
            )

        messages = await run_blocking_io(
            self.career_repo.get_messages_by_session,
            session_id,
            user_id,
            skip,
            limit,
        )

        return [
            self._serialize_message(message)
            for message in messages
        ]

    async def _get_or_create_session(
        self,
        user_id: int,
        session_id: Optional[int],
        question: str,
        target_role: Optional[str],
    ):
        if session_id is not None:
            session = await run_blocking_io(
                self.career_repo.get_session_by_id,
                session_id,
                user_id,
            )

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Career coach session not found",
                )

            return session

        title = question[:80]

        if len(question) > 80:
            title = f"{title}..."

        session = await run_blocking_io(
            self.career_repo.create_session,
            {
                "user_id": user_id,
                "title": title,
                "target_role": target_role,
                "is_active": True,
            },
        )

        return session

    async def _retrieve_context_chunks(
        self,
        user_id: int,
        question: str,
        top_k: int,
    ) -> list[dict[str, Any]]:
        chunks = await run_blocking_io(
            self.rag_repo.get_chunks_by_user,
            user_id,
        )

        if not chunks:
            return []

        query_embedding = await self.rag_engine.embed_text(
            question
        )

        if not query_embedding:
            return []

        scored_chunks: list[dict[str, Any]] = []

        for chunk in chunks:
            try:
                chunk_embedding = json.loads(
                    chunk.embedding_json
                )
            except json.JSONDecodeError:
                logger.warning(
                    "Invalid embedding_json for chunk_id=%s",
                    chunk.id,
                )
                continue

            similarity = self.rag_engine.cosine_similarity(
                first_vector=query_embedding,
                second_vector=chunk_embedding,
            )

            scored_chunks.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": round(
                        similarity,
                        6,
                    ),
                }
            )

        return sorted(
            scored_chunks,
            key=lambda item: item["similarity"],
            reverse=True,
        )[:top_k]

    def _build_conversation_history(
        self,
        messages,
    ) -> str:
        lines: list[str] = []

        for message in messages:
            lines.append(
                f"{message.role}: {message.content}"
            )

        return "\n".join(lines)

    def _serialize_session(
        self,
        session,
    ) -> dict[str, Any]:
        return {
            "id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "target_role": session.target_role,
            "is_active": session.is_active,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }

    def _serialize_message(
        self,
        message,
    ) -> dict[str, Any]:
        return {
            "id": message.id,
            "user_id": message.user_id,
            "session_id": message.session_id,
            "role": message.role,
            "content": message.content,
            "context_chunks": message.context_chunks,
            "provider": message.provider,
            "model_name": message.model_name,
            "created_at": message.created_at,
        }