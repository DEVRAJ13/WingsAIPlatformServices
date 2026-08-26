from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph
from app.api.dependencies import get_current_user, get_db
from app.services.workflow_service import WorkflowService
from app.schemas.rag import (
    AgentQueryRequest,
    AgentQueryResponse,
)

router = APIRouter()


@router.post(
    "/query",
    response_model=AgentQueryResponse,
)
async def agent_query(
    request: AgentQueryRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentQueryResponse:

    workflow_service = WorkflowService(db)
    run = await workflow_service.start(user_id=current_user.id, question=request.question)
    graph = build_agent_graph(db)

    initial_state = {
        "user_id": current_user.id,
        "workflow_id": run.workflow_id,
        "question": request.question,
        "incident_id": request.incident_id,
    }

    try:
        result = await graph.ainvoke(initial_state)
    except (RuntimeError, ValueError) as exc:
        await workflow_service.finish(run.workflow_id, status="FAILED", error=str(exc))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        await workflow_service.finish(run.workflow_id, status="FAILED", error="AI agent service is temporarily unavailable.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI agent service is temporarily unavailable.") from exc

    final_status = "WAITING_FOR_APPROVAL" if result.get("approval_id") else "COMPLETED"
    await workflow_service.finish(run.workflow_id, status=final_status)

    return AgentQueryResponse(
        answer=result.get("answer", ""),
        intent=result.get("intent", "knowledge"),
        sources=result.get("sources", []),
        diagnosis=result.get("diagnosis"),
        workflow_id=run.workflow_id,
        approval_id=result.get("approval_id"),
        workflow_status=final_status,
    )