from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.approval_service import ApprovalService


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


class CreateAIApprovalRequest(BaseModel):
    tool_name: str = Field(
        min_length=1,
        max_length=100,
    )

    reason: str = Field(
        min_length=1,
        max_length=2000,
    )

    parameters: dict


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(
        min_length=1,
        max_length=20,
    )

    decision_comment: str | None = Field(
        default=None,
        max_length=2000,
    )


@router.post(
    "/from-ai",
    status_code=status.HTTP_201_CREATED,
)
async def create_ai_approval(
    request: CreateAIApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval_service = ApprovalService(db)

    try:
        approval = await approval_service.request_approval(
            tool_name=request.tool_name,
            requested_by=current_user.id,
            reason=request.reason,
            parameters=request.parameters,
        )

        return {
            "success": True,
            "message": (
                "Approval request created. "
                "Human approval is required."
            ),
            "approval": approval,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{approval_id}/decide",
)
async def decide_approval(
    approval_id: int,
    request: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval_service = ApprovalService(db)

    try:
        result = await approval_service.decide(
            approval_id=approval_id,
            decision=request.decision.upper(),
            decision_by=current_user.id,
            decision_comment=request.decision_comment,
        )

        return {
            "success": True,
            "message": (
                "Approval request "
                f"{result['status'].lower()}."
            ),
            "approval": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc