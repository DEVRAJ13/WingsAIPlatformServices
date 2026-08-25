from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user, get_db
from app.core.rbac import can_execute
from app.models.user import User
from app.services.tool_execution_service import ToolExecutionService

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/{approval_id}/execute")
async def execute_approved_tool(approval_id: int, db=Depends(get_db), current_user: User = Depends(get_current_user)):
    if not can_execute(current_user):
        raise HTTPException(status_code=403, detail="Your role is not authorized to execute operational actions.")
    service = ToolExecutionService(db)
    try:
        result = await service.execute_approved(approval_id=approval_id, executed_by=current_user.id)
        return {"success": True, "execution": result}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
