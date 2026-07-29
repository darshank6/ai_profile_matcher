from typing import List
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.rag import RAGChunk
from app.models.rag import RAGDocument
from app.models.rag import RAGQueryReport


class RAGRepository:
    """
    Repository layer for RAG documents, chunks and query reports.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create_document(
        self,
        document_data: dict,
    ) -> RAGDocument:
        document = RAGDocument(**document_data)

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def update_document(
        self,
        document: RAGDocument,
        update_data: dict,
    ) -> RAGDocument:
        for key, value in update_data.items():
            if value is not None:
                setattr(document, key, value)

        self.db.commit()
        self.db.refresh(document)

        return document

    def get_document_by_id(
        self,
        document_id: int,
        user_id: int,
    ) -> Optional[RAGDocument]:
        return (
            self.db.query(RAGDocument)
            .filter(RAGDocument.id == document_id)
            .filter(RAGDocument.user_id == user_id)
            .first()
        )

    def get_documents_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[RAGDocument]:
        return (
            self.db.query(RAGDocument)
            .filter(RAGDocument.user_id == user_id)
            .order_by(RAGDocument.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_documents(
        self,
        user_id: int,
        search: str,
        skip: int = 0,
        limit: int = 10,
    ) :
        search_pattern = f"%{search}%"

        return (
            self.db.query(RAGDocument)
            .filter(RAGDocument.user_id == user_id)
            .filter(
                or_(
                    RAGDocument.title.ilike(search_pattern),
                    RAGDocument.source_type.ilike(search_pattern),
                    RAGDocument.content.ilike(search_pattern),
                )
            )
            .order_by(RAGDocument.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_document(
        self,
        document: RAGDocument,
    ) -> bool:
        self.db.delete(document)
        self.db.commit()

        return True

    def batch_delete_documents(
        self,
        user_id: int,
        document_ids: List[int],
    ) -> int:
        documents = (
            self.db.query(RAGDocument)
            .filter(RAGDocument.user_id == user_id)
            .filter(RAGDocument.id.in_(document_ids))
            .all()
        )

        deleted_count = len(documents)

        for document in documents:
            self.db.delete(document)

        self.db.commit()

        return deleted_count

    def create_chunks(
        self,
        chunks_data: List[dict],
    ) :
        chunks = [
            RAGChunk(**chunk_data)
            for chunk_data in chunks_data
        ]

        self.db.add_all(chunks)
        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks

    def delete_chunks_by_document_id(
        self,
        document_id: int,
        user_id: int,
    ) -> int:
        chunks = (
            self.db.query(RAGChunk)
            .filter(RAGChunk.document_id == document_id)
            .filter(RAGChunk.user_id == user_id)
            .all()
        )

        deleted_count = len(chunks)

        for chunk in chunks:
            self.db.delete(chunk)

        self.db.commit()

        return deleted_count

    def get_chunks_by_user(
        self,
        user_id: int,
    ) -> List[RAGChunk]:
        return (
            self.db.query(RAGChunk)
            .filter(RAGChunk.user_id == user_id)
            .all()
        )

    def get_chunks_by_document(
        self,
        document_id: int,
        user_id: int,
    ) -> List[RAGChunk]:
        return (
            self.db.query(RAGChunk)
            .filter(RAGChunk.document_id == document_id)
            .filter(RAGChunk.user_id == user_id)
            .order_by(RAGChunk.chunk_index.asc())
            .all()
        )

    def create_query_report(
        self,
        report_data: dict,
    ) -> RAGQueryReport:
        report = RAGQueryReport(**report_data)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_query_report_by_id(
        self,
        report_id: int,
        user_id: int,
    ) -> Optional[RAGQueryReport]:
        return (
            self.db.query(RAGQueryReport)
            .filter(RAGQueryReport.id == report_id)
            .filter(RAGQueryReport.user_id == user_id)
            .first()
        )

    def get_query_reports_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[RAGQueryReport]:
        return (
            self.db.query(RAGQueryReport)
            .filter(RAGQueryReport.user_id == user_id)
            .order_by(RAGQueryReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_query_report(
        self,
        report: RAGQueryReport,
    ) -> bool:
        self.db.delete(report)
        self.db.commit()

        return True