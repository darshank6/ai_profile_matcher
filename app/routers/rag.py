from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.rag import RAGAskRequest
from app.schemas.rag import RAGBatchDeleteRequest
from app.schemas.rag import RAGBatchDeleteResponse
from app.schemas.rag import RAGDeleteResponse
from app.schemas.rag import RAGDocumentCreateRequest
from app.schemas.rag import RAGDocumentResponse
from app.schemas.rag import RAGDocumentUpdateRequest
from app.schemas.rag import RAGQueryReportResponse
from app.services.rag_service import RAGService


router = APIRouter()


@router.post(
    "/documents",
    response_model=RAGDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create RAG document",
)
def create_rag_document(
    request: RAGDocumentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.create_document(
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        source_type=request.source_type,
        source_id=request.source_id,
    )


@router.get(
    "/documents",
    response_model=List[RAGDocumentResponse],
    summary="List RAG documents",
)
def list_rag_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.get_my_documents(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/documents/search",
    response_model=List[RAGDocumentResponse],
    summary="Search RAG documents",
)
def search_rag_documents(
    query: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.search_documents(
        user_id=current_user.id,
        search=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/documents/{document_id}",
    response_model=RAGDocumentResponse,
    summary="Get RAG document",
)
def get_rag_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.get_document(
        user_id=current_user.id,
        document_id=document_id,
    )


@router.put(
    "/documents/{document_id}",
    response_model=RAGDocumentResponse,
    summary="Update RAG document",
)
def update_rag_document(
    document_id: int,
    request: RAGDocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.update_document(
        user_id=current_user.id,
        document_id=document_id,
        update_data=request.model_dump(),
    )


@router.delete(
    "/documents/{document_id}",
    response_model=RAGDeleteResponse,
    summary="Delete RAG document",
)
def delete_rag_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.delete_document(
        user_id=current_user.id,
        document_id=document_id,
    )


@router.post(
    "/documents/batch-delete",
    response_model=RAGBatchDeleteResponse,
    summary="Batch delete RAG documents",
)
def batch_delete_rag_documents(
    request: RAGBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.batch_delete_documents(
        user_id=current_user.id,
        document_ids=request.document_ids,
    )


@router.post(
    "/ask",
    response_model=RAGQueryReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ask question using RAG",
)
def ask_rag_question(
    request: RAGAskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.ask_question(
        user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
        provider=request.provider,
        model_name=request.model_name,
    )


@router.get(
    "/query-reports",
    response_model=List[RAGQueryReportResponse],
    summary="List RAG query reports",
)
def list_rag_query_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.get_my_query_reports(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/query-reports/{report_id}",
    response_model=RAGQueryReportResponse,
    summary="Get RAG query report",
)
def get_rag_query_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.get_query_report(
        user_id=current_user.id,
        report_id=report_id,
    )


@router.delete(
    "/query-reports/{report_id}",
    response_model=RAGDeleteResponse,
    summary="Delete RAG query report",
)
def delete_rag_query_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RAGService(db)

    return service.delete_query_report(
        user_id=current_user.id,
        report_id=report_id,
    )