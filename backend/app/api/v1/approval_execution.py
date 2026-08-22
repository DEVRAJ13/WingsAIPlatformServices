from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.tool_execution_service import (
    ToolExecutionService,
)


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


@router.post(
    "/{approval_id}/execute",
)
async def execute_approved_tool(
    approval_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ToolExecutionService(db)

    try:
        result = await service.execute_approved(
            approval_id=approval_id,
            executed_by=current_user.id,
        )

        return {
            "success": True,
            "execution": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc