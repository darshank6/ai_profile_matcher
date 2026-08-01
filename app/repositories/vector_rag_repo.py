from typing import List
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.vector_rag import VectorRAGChunk
from app.models.vector_rag import VectorRAGDocument
from app.models.vector_rag import VectorRAGQueryReport


class VectorRAGRepository:
    """
    Repository layer for PgVector RAG documents, chunks, and query reports.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(self, document_data: dict) -> VectorRAGDocument:
        document = VectorRAGDocument(**document_data)

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def update_document(
        self,
        document: VectorRAGDocument,
        update_data: dict,
    ) -> VectorRAGDocument:
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
    ) -> Optional[VectorRAGDocument]:
        return (
            self.db.query(VectorRAGDocument)
            .filter(VectorRAGDocument.id == document_id)
            .filter(VectorRAGDocument.user_id == user_id)
            .first()
        )

    def get_documents_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[VectorRAGDocument]:
        return (
            self.db.query(VectorRAGDocument)
            .filter(VectorRAGDocument.user_id == user_id)
            .order_by(VectorRAGDocument.created_at.desc())
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
    ) -> List[VectorRAGDocument]:
        search_pattern = f"%{search}%"

        return (
            self.db.query(VectorRAGDocument)
            .filter(VectorRAGDocument.user_id == user_id)
            .filter(
                or_(
                    VectorRAGDocument.title.ilike(search_pattern),
                    VectorRAGDocument.source_type.ilike(search_pattern),
                    VectorRAGDocument.content.ilike(search_pattern),
                )
            )
            .order_by(VectorRAGDocument.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_document(self, document: VectorRAGDocument) -> bool:
        self.db.delete(document)
        self.db.commit()

        return True

    def batch_delete_documents(
        self,
        user_id: int,
        document_ids: List[int],
    ) -> int:
        documents = (
            self.db.query(VectorRAGDocument)
            .filter(VectorRAGDocument.user_id == user_id)
            .filter(VectorRAGDocument.id.in_(document_ids))
            .all()
        )

        deleted_count = len(documents)

        for document in documents:
            self.db.delete(document)

        self.db.commit()

        return deleted_count

    def create_chunks(self, chunks_data: List[dict]) -> List[VectorRAGChunk]:
        chunks = [
            VectorRAGChunk(**chunk_data)
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
            self.db.query(VectorRAGChunk)
            .filter(VectorRAGChunk.document_id == document_id)
            .filter(VectorRAGChunk.user_id == user_id)
            .all()
        )

        deleted_count = len(chunks)

        for chunk in chunks:
            self.db.delete(chunk)

        self.db.commit()

        return deleted_count

    def search_similar_chunks(
        self,
        user_id: int,
        query_embedding: List[float],
        top_k: int,
    ) -> List[VectorRAGChunk]:
        return (
            self.db.query(VectorRAGChunk)
            .filter(VectorRAGChunk.user_id == user_id)
            .order_by(VectorRAGChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )

    def create_query_report(
        self,
        report_data: dict,
    ) -> VectorRAGQueryReport:
        report = VectorRAGQueryReport(**report_data)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_query_report_by_id(
        self,
        report_id: int,
        user_id: int,
    ) -> Optional[VectorRAGQueryReport]:
        return (
            self.db.query(VectorRAGQueryReport)
            .filter(VectorRAGQueryReport.id == report_id)
            .filter(VectorRAGQueryReport.user_id == user_id)
            .first()
        )

    def get_query_reports_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[VectorRAGQueryReport]:
        return (
            self.db.query(VectorRAGQueryReport)
            .filter(VectorRAGQueryReport.user_id == user_id)
            .order_by(VectorRAGQueryReport.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_query_report(self, report: VectorRAGQueryReport) -> bool:
        self.db.delete(report)
        self.db.commit()

        return True