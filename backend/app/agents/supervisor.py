from app.agents.state import AgentState


KNOWLEDGE_KEYWORDS = (
    "what is",
    "what are",
    "what should",
    "explain",
    "how does",
    "how do",
    "why",
    "policy",
    "procedure",
    "guide",
    "documentation",
    "document",
    "process",
    "meaning",
    "definition",
)


INCIDENT_KEYWORDS = (
    "diagnose incident",
    "diagnosis of incident",
    "investigate incident",
    "investigate the incident",
    "incident id",
    "incident_id",
    "incident number",
    "incident status",
    "incident details",
    "troubleshoot incident",
    "analyze incident",
    "analyse incident",
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

    if not text:
        return "knowledge"

    # ---------------------------------------------------------
    # ITSM
    # ---------------------------------------------------------

    if any(
        keyword in text
        for keyword in ITSM_KEYWORDS
    ):
        return "itsm"

    # ---------------------------------------------------------
    # SPECIFIC INCIDENT OPERATIONS
    #
    # Do NOT classify every question containing "incident"
    # as an incident workflow.
    # ---------------------------------------------------------

    if any(
        keyword in text
        for keyword in INCIDENT_KEYWORDS
    ):
        return "incident"

    # ---------------------------------------------------------
    # GENERAL KNOWLEDGE
    # ---------------------------------------------------------

    if any(
        keyword in text
        for keyword in KNOWLEDGE_KEYWORDS
    ):
        return "knowledge"

    # ---------------------------------------------------------
    # GENERAL QUESTIONS
    #
    # If there is no explicit operational intent,
    # safely default to knowledge.
    # ---------------------------------------------------------

    return "knowledge"


def supervisor(
    state: AgentState,
) -> AgentState:
    question = state.get(
        "question",
        "",
    )

    intent = classify_intent(question)

    return {
        **state,
        "intent": intent,
        "next_node": intent,
    }