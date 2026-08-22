from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.rag import RAGQueryResponse
from app.services.rag_service import RAGService

from app.api.dependencies import get_current_user, get_db
from app.schemas.rag import (
    DocumentCreateRequest,
    DocumentCreateResponse,
    RAGQueryRequest,
)
from app.services.knowledge_service import KnowledgeService
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post(
    "/documents",
    response_model=DocumentCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    request: DocumentCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentCreateResponse:

    service = KnowledgeService(db)

    document_id, chunks_created = (
        await service.ingest_document(
            title=request.title,
            content=request.content,
        )
    )

    return DocumentCreateResponse(
        id=document_id,
        title=request.title,
        chunks_created=chunks_created,
    )


@router.post("/rag/search")
async def search_knowledge(
    request: RAGQueryRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    service = RetrievalService(db)

    results = await service.search(
        question=request.question,
        limit=5,
    )

    return {
        "question": request.question,
        "results": results,
    }

@router.post(
    "/rag/query",
    response_model=RAGQueryResponse,
)
async def rag_query(
    request: RAGQueryRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RAGQueryResponse:

    service = RAGService(db)

    answer, results = await service.query(
        question=request.question,
        top_k=3,
    )

    sources = [
        {
            "document_id": result["document_id"],
            "document_title": result["document_title"],
            "chunk_id": result["chunk_id"],
            "chunk_index": result["chunk_index"],
            "distance": result["distance"],
        }
        for result in results
    ]

    return RAGQueryResponse(
        answer=answer,
        sources=sources,
        model="qwen2.5:1.5b",
    )