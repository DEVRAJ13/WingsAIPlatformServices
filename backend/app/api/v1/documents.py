from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


class CreateDocumentRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    content: str = Field(
        min_length=1,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    request: CreateDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create and index an enterprise document.

    Flow:

    Document
        ↓
    Chunk
        ↓
    Ollama embedding
        ↓
    pgvector
    """

    _ = current_user

    service = DocumentService(db)

    try:
        result = await service.create_document(
            title=request.title,
            content=request.content,
        )

        return {
            "success": True,
            "document": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc