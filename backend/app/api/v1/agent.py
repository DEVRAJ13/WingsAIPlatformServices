from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph
from app.api.dependencies import get_current_user, get_db
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

    graph = build_agent_graph(db)

    # ADD THIS HERE
    initial_state = {
        "user_id": current_user.id,
        "question": request.question,
        "incident_id": request.incident_id,
    }

    result = await graph.ainvoke(
        initial_state
    )

    return AgentQueryResponse(
        answer=result.get("answer", ""),
        intent=result.get("intent", "knowledge"),
        sources=result.get("sources", []),
        diagnosis=result.get("diagnosis"),
    )