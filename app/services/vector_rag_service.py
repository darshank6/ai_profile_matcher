import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from fastapi import HTTPException
from fastapi import status

from app.ai.llm_client import LLMClient
from app.ai.rag_engine import RAGEngine
from app.config import settings
from app.repositories.vector_rag_repo import VectorRAGRepository


logger = logging.getLogger(__name__)


class VectorRAGService:
    """
    Service layer for PgVector-backed RAG.
    """

    def __init__(self, db) -> None:
        self.vector_repo = VectorRAGRepository(db)
        self.rag_engine = RAGEngine()

    def create_document(
        self,
        user_id: int,
        title: str,
        content: str,
        source_type: str = "manual",
        source_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        cleaned_title = title.strip()
        cleaned_content = content.strip()
        cleaned_source_type = source_type.strip()

        if not cleaned_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document title cannot be empty",
            )

        if not cleaned_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document content cannot be empty",
            )

        chunks = self.rag_engine.chunk_text(cleaned_content)

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create chunks from document content",
            )

        document_data = {
            "user_id": user_id,
            "title": cleaned_title,
            "source_type": cleaned_source_type,
            "source_id": source_id,
            "content": cleaned_content,
            "chunk_count": len(chunks),
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "embedding_model": settings.EMBEDDING_MODEL,
        }

        document = self.vector_repo.create_document(document_data)

        chunk_rows: List[dict] = []

        for index, chunk in enumerate(chunks):
            embedding = self.rag_engine.embed_text(chunk)

            if not embedding:
                continue

            chunk_rows.append(
                {
                    "user_id": user_id,
                    "document_id": document.id,
                    "chunk_index": index,
                    "content": chunk,
                    "token_count": len(chunk.split()),
                    "embedding": embedding,
                }
            )

        if not chunk_rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embeddings for document chunks",
            )

        self.vector_repo.create_chunks(chunk_rows)

        logger.info(
            "Vector RAG document created | user_id=%s document_id=%s chunks=%s",
            user_id,
            document.id,
            len(chunk_rows),
        )

        refreshed_document = self.vector_repo.get_document_by_id(
            document_id=document.id,
            user_id=user_id,
        )

        if refreshed_document is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reload vector RAG document",
            )

        return self._serialize_document(refreshed_document)

    def update_document(
        self,
        user_id: int,
        document_id: int,
        update_data: dict,
    ) -> Dict[str, Any]:
        document = self.vector_repo.get_document_by_id(
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vector RAG document not found",
            )

        safe_update_data: Dict[str, Any] = {}

        if update_data.get("title") is not None:
            title = update_data["title"].strip()

            if not title:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document title cannot be empty",
                )

            safe_update_data["title"] = title

        if update_data.get("content") is not None:
            new_content = update_data["content"].strip()

            if not new_content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document content cannot be empty",
                )

            chunks = self.rag_engine.chunk_text(new_content)

            if not chunks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to create chunks from updated content",
                )

            self.vector_repo.delete_chunks_by_document_id(
                document_id=document_id,
                user_id=user_id,
            )

            chunk_rows: List[dict] = []

            for index, chunk in enumerate(chunks):
                embedding = self.rag_engine.embed_text(chunk)

                if not embedding:
                    continue

                chunk_rows.append(
                    {
                        "user_id": user_id,
                        "document_id": document_id,
                        "chunk_index": index,
                        "content": chunk,
                        "token_count": len(chunk.split()),
                        "embedding": embedding,
                    }
                )

            if not chunk_rows:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to regenerate embeddings for updated document",
                )

            self.vector_repo.create_chunks(chunk_rows)

            safe_update_data["content"] = new_content
            safe_update_data["chunk_count"] = len(chunk_rows)
            safe_update_data["embedding_provider"] = settings.EMBEDDING_PROVIDER
            safe_update_data["embedding_model"] = settings.EMBEDDING_MODEL

        updated_document = self.vector_repo.update_document(
            document=document,
            update_data=safe_update_data,
        )

        return self._serialize_document(updated_document)

    def get_document(
        self,
        user_id: int,
        document_id: int,
    ) -> Dict[str, Any]:
        document = self.vector_repo.get_document_by_id(
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vector RAG document not found",
            )

        return self._serialize_document(document)

    def get_my_documents(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        documents = self.vector_repo.get_documents_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        return [
            self._serialize_document(document)
            for document in documents
        ]

    def search_documents(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        cleaned_search = search.strip()

        if not cleaned_search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty",
            )

        documents = self.vector_repo.search_documents(
            user_id=user_id,
            search=cleaned_search,
            skip=skip,
            limit=limit,
        )

        return [
            self._serialize_document(document)
            for document in documents
        ]

    def delete_document(
        self,
        user_id: int,
        document_id: int,
    ) -> Dict[str, str]:
        document = self.vector_repo.get_document_by_id(
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vector RAG document not found",
            )

        self.vector_repo.delete_document(document)

        return {
            "message": "Vector RAG document deleted successfully"
        }

    def batch_delete_documents(
        self,
        user_id: int,
        document_ids: List[int],
    ) -> Dict[str, Any]:
        if not document_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document_ids cannot be empty",
            )

        deleted_count = self.vector_repo.batch_delete_documents(
            user_id=user_id,
            document_ids=document_ids,
        )

        return {
            "deleted_count": deleted_count,
            "message": f"{deleted_count} vector RAG document(s) deleted successfully",
        }

    def ask_question(
        self,
        user_id: int,
        question: str,
        top_k: int = 5,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        cleaned_question = question.strip()

        if not cleaned_question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty",
            )

        query_embedding = self.rag_engine.embed_text(cleaned_question)

        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate question embedding",
            )

        top_chunks = self.vector_repo.search_similar_chunks(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=top_k,
        )

        if not top_chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant vector chunks found",
            )

        matched_chunks = []

        for chunk in top_chunks:
            matched_chunks.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                }
            )

        context = "\n\n".join(
            chunk.content
            for chunk in top_chunks
        )

        final_provider = provider or settings.LLM_PROVIDER
        final_model_name = model_name or settings.LLM_MODEL

        llm_client = LLMClient(
            provider=final_provider,
            model_name=final_model_name,
        )

        answer = llm_client.generate_rag_answer(
            question=cleaned_question,
            context=context,
        )

        report_data = {
            "user_id": user_id,
            "question": cleaned_question,
            "answer": answer,
            "matched_chunks": json.dumps(
                matched_chunks,
                ensure_ascii=False,
            ),
            "provider": final_provider,
            "model_name": final_model_name,
        }

        report = self.vector_repo.create_query_report(report_data)

        return self._serialize_query_report(report)

    def get_my_query_reports(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        reports = self.vector_repo.get_query_reports_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        return [
            self._serialize_query_report(report)
            for report in reports
        ]

    def get_query_report(
        self,
        user_id: int,
        report_id: int,
    ) -> Dict[str, Any]:
        report = self.vector_repo.get_query_report_by_id(
            report_id=report_id,
            user_id=user_id,
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vector RAG query report not found",
            )

        return self._serialize_query_report(report)

    def delete_query_report(
        self,
        user_id: int,
        report_id: int,
    ) -> Dict[str, str]:
        report = self.vector_repo.get_query_report_by_id(
            report_id=report_id,
            user_id=user_id,
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vector RAG query report not found",
            )

        self.vector_repo.delete_query_report(report)

        return {
            "message": "Vector RAG query report deleted successfully"
        }

    def _serialize_document(self, document) -> Dict[str, Any]:
        return {
            "id": document.id,
            "user_id": document.user_id,
            "title": document.title,
            "source_type": document.source_type,
            "source_id": document.source_id,
            "content": document.content,
            "chunk_count": document.chunk_count,
            "embedding_provider": document.embedding_provider,
            "embedding_model": document.embedding_model,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
        }

    def _serialize_query_report(self, report) -> Dict[str, Any]:
        return {
            "id": report.id,
            "user_id": report.user_id,
            "question": report.question,
            "answer": report.answer,
            "matched_chunks": report.matched_chunks,
            "provider": report.provider,
            "model_name": report.model_name,
            "created_at": report.created_at,
        }