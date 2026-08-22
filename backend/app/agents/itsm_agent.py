from app.agents.state import AgentState


async def itsm_agent(
    state: AgentState,
) -> AgentState:

    return {
        **state,
        "answer": (
            "ITSM integration is not yet configured. "
            "No ticket or change request was created."
        ),
        "sources": [],
    }