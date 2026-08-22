from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.services.rag_service import RAGService


async def knowledge_agent(
    state: AgentState,
    db: AsyncSession,
) -> AgentState:

    service = RAGService(db)

    answer, sources = await service.query(
        question=state["question"],
        top_k=3,
    )

    return {
        **state,
        "answer": answer,
        "sources": sources,
    }