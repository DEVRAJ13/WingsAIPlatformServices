from app.agents.state import AgentState


async def itsm_agent(state: AgentState) -> AgentState:
    question = state.get("question", "").strip()
    text = question.lower()

    provider = "servicenow" if "servicenow" in text or "service now" in text else "jira"
    if "remedy" in text:
        provider = "remedy"

    action = (
        "change request"
        if "change" in text
        else "service request"
        if "service request" in text
        else "incident/ticket"
    )

    priority = "HIGH" if any(x in text for x in ("critical", "p1", "urgent", "high priority")) else "MEDIUM"

    recommendation = {
        "should_create_ticket": True,
        "provider": provider,
        "action": action,
        "title": question[:180],
        "description": question,
        "priority": priority,
        "requires_human_approval": True,
        "risk_level": "HIGH" if action == "change request" else "MEDIUM",
    }

    return {
        **state,
        "answer": (
            f"WINGS recommends a {action} for {provider.title()}. "
            "No external action has been executed. Human approval is required."
        ),
        "itsm_recommendation": recommendation,
        "sources": [],
    }
