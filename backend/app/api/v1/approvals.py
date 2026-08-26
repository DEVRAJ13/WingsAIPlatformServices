from fastapi import APIRouter, Depends, HTTPException, status
import json
from sqlalchemy import select
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.approval_request import ApprovalRequest
from app.services.approval_service import ApprovalService
from app.core.rbac import can_approve, can_execute


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


@router.get("")
async def list_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ApprovalRequest)
        .order_by(ApprovalRequest.id.desc())
        .limit(100)
    )
    approvals = result.scalars().all()
    return {
        "success": True,
        "approvals": [
            {
                "id": item.id,
                "workflow_id": item.workflow_id,
                "tool_name": item.tool_name,
                "status": item.status,
                "reason": item.reason,
                "parameters": json.loads(item.parameters or "{}"),
                "requested_by": item.requested_by,
                "decision_by": item.decision_by,
                "decision_comment": item.decision_comment,
                "created_at": item.created_at,
                "decided_at": item.decided_at,
                "can_decide": can_approve(current_user) and item.status == "PENDING" and item.requested_by != current_user.id,
                "can_execute": can_execute(current_user) and item.status == "APPROVED" and item.requested_by != current_user.id and item.decision_by != current_user.id,
            }
            for item in approvals
        ],
    }


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

    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


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
            decision_user=current_user,
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