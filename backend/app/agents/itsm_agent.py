from app.agents.state import AgentState


async def itsm_agent(state: AgentState) -> AgentState:
    question = state.get("question", "").strip()
    text = question.lower()
    provider = "servicenow" if "servicenow" in text or "service now" in text else "jira"
    if "remedy" in text:
        provider = "remedy"

    action = "change request" if "change" in text else "service request" if "service request" in text else "incident/ticket"
    return {
        **state,
        "answer": (
            f"WINGS can prepare a {action} for {provider.title()}. "
            "No external ticket has been created. Human approval is required before execution."
        ),
        "itsm_recommendation": {
            "should_create_ticket": True,
            "provider": provider,
            "title": question[:180],
            "description": question,
            "priority": "MEDIUM",
        },
        "sources": [],
    }
