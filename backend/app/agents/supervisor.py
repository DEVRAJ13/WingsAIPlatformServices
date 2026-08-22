from app.agents.state import AgentState


KNOWLEDGE_KEYWORDS = (
    "what is",
    "explain",
    "how does",
    "policy",
    "procedure",
    "guide",
    "documentation",
    "document",
)

INCIDENT_KEYWORDS = (
    "incident",
    "error",
    "failure",
    "outage",
    "down",
    "not working",
)

ITSM_KEYWORDS = (
    "ticket",
    "servicenow",
    "service now",
    "jira",
    "change request",
    "service request",
)


def classify_intent(question: str) -> str:
    text = question.lower().strip()

    if any(keyword in text for keyword in ITSM_KEYWORDS):
        return "itsm"

    if any(keyword in text for keyword in INCIDENT_KEYWORDS):
        return "incident"

    if any(keyword in text for keyword in KNOWLEDGE_KEYWORDS):
        return "knowledge"

    return "knowledge"


def supervisor(state: AgentState) -> AgentState:
    intent = classify_intent(state["question"])

    return {
        **state,
        "intent": intent,
    }