from typing import Any, TypedDict


class AgentState(TypedDict, total=False):

    user_id: int

    question: str

    incident_id: int | None

    intent: str

    answer: str

    diagnosis: dict[str, Any]

    itsm_recommendation: dict[str, Any]

    approval_id: int | None

    tool_result: dict[str, Any]

    error: str | None