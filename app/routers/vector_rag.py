from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.vector_rag import VectorRAGAskRequest
from app.schemas.vector_rag import VectorRAGBatchDeleteRequest
from app.schemas.vector_rag import VectorRAGBatchDeleteResponse
from app.schemas.vector_rag import VectorRAGDeleteResponse
from app.schemas.vector_rag import VectorRAGDocumentCreateRequest
from app.schemas.vector_rag import VectorRAGDocumentResponse
from app.schemas.vector_rag import VectorRAGDocumentUpdateRequest
from app.schemas.vector_rag import VectorRAGQueryReportResponse
from app.services.vector_rag_service import VectorRAGService


router = APIRouter()


@router.post(
    "/documents",
    response_model=VectorRAGDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create PgVector RAG document",
)
def create_vector_rag_document(
    request: VectorRAGDocumentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.create_document(
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        source_type=request.source_type,
        source_id=request.source_id,
    )


@router.get(
    "/documents",
    response_model=List[VectorRAGDocumentResponse],
    summary="List PgVector RAG documents",
)
def list_vector_rag_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.get_my_documents(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/documents/search",
    response_model=List[VectorRAGDocumentResponse],
    summary="Search PgVector RAG documents",
)
def search_vector_rag_documents(
    query: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.search_documents(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/documents/{document_id}",
    response_model=VectorRAGDocumentResponse,
    summary="Get PgVector RAG document",
)
def get_vector_rag_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.get_document(
        user_id=current_user.id,
        document_id=document_id,
    )


@router.put(
    "/documents/{document_id}",
    response_model=VectorRAGDocumentResponse,
    summary="Update PgVector RAG document",
)
def update_vector_rag_document(
    document_id: int,
    request: VectorRAGDocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.update_document(
        user_id=current_user.id,
        document_id=document_id,
        update_data=request.model_dump(),
    )


@router.delete(
    "/documents/{document_id}",
    response_model=VectorRAGDeleteResponse,
    summary="Delete PgVector RAG document",
)
def delete_vector_rag_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.delete_document(
        user_id=current_user.id,
        document_id=document_id,
    )


@router.post(
    "/documents/batch-delete",
    response_model=VectorRAGBatchDeleteResponse,
    summary="Batch delete PgVector RAG documents",
)
def batch_delete_vector_rag_documents(
    request: VectorRAGBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.batch_delete_documents(
        user_id=current_user.id,
        document_ids=request.document_ids,
    )


@router.post(
    "/ask",
    response_model=VectorRAGQueryReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ask question using PgVector RAG",
)
def ask_vector_rag_question(
    request: VectorRAGAskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.ask_question(
        user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
        provider=request.provider,
        model_name=request.model_name,
    )


@router.get(
    "/query-reports",
    response_model=List[VectorRAGQueryReportResponse],
    summary="List PgVector RAG query reports",
)
def list_vector_rag_query_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.get_my_query_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/query-reports/{report_id}",
    response_model=VectorRAGQueryReportResponse,
    summary="Get PgVector RAG query report",
)
def get_vector_rag_query_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.get_query_report(
        user_id=current_user.id,
        report_id=report_id,
    )


@router.delete(
    "/query-reports/{report_id}",
    response_model=VectorRAGDeleteResponse,
    summary="Delete PgVector RAG query report",
)
def delete_vector_rag_query_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = VectorRAGService(db)

    return service.delete_query_report(
        user_id=current_user.id,
        report_id=report_id,
    )