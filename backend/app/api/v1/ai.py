import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.config import ALLOWED_AI_MODEL
from app.ai.schemas import AIChatRequest, AIChatResponse
from app.api.dependencies import get_current_user
from app.services.ai_service import AIService


logger = logging.getLogger(__name__)

router = APIRouter()

ai_service = AIService()


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
async def chat(
    request: AIChatRequest,
    current_user=Depends(get_current_user),
) -> AIChatResponse:

    try:
        answer = await ai_service.chat(
            request.message,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "AI generation failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable.",
        ) from exc

    return AIChatResponse(
        answer=answer,
        model=ALLOWED_AI_MODEL,
    )