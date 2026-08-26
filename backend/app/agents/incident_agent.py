from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.services.incident_diagnosis_service import IncidentDiagnosisService
from app.services.vector_search_service import VectorSearchService
from app.tools.factory import build_tool_registry


async def incident_agent(
    state: AgentState,
    db: AsyncSession,
) -> AgentState:

    incident_id = state.get(
        "incident_id"
    )

    # ---------------------------------------------------------
    # INCIDENT ID VALIDATION
    # ---------------------------------------------------------

    if not incident_id:
        return {
            **state,
            "answer": (
                "Please provide an incident ID "
                "for diagnosis."
            ),
            "sources": [],
        }

    # ---------------------------------------------------------
    # TOOL REGISTRY
    # ---------------------------------------------------------

    registry = build_tool_registry(
        db
    )

    get_incident_tool = registry.get(
        "get_incident"
    )

    if get_incident_tool is None:
        return {
            **state,
            "answer": (
                "Incident retrieval tool "
                "is unavailable."
            ),
            "sources": [],
        }

    # ---------------------------------------------------------
    # GET INCIDENT THROUGH TOOL
    # ---------------------------------------------------------

    tool_result = await get_incident_tool.execute(
        incident_id=incident_id
    )

    if not tool_result.get("success"):
        return {
            **state,
            "answer": tool_result.get(
                "message",
                "Incident not found.",
            ),
            "sources": [],
        }

    incident = tool_result.get(
        "incident"
    )

    if not incident:
        return {
            **state,
            "answer": "Incident details were not returned.",
            "sources": [],
        }

    # ---------------------------------------------------------
    # RAG + AI DIAGNOSIS
    # ---------------------------------------------------------

    # Retrieve enterprise knowledge as supporting evidence. RAG failure is
    # non-fatal: diagnosis can still proceed using incident data alone.
    knowledge_results = []
    try:
        search = VectorSearchService(db)
        knowledge_results = await search.search(
            query=f"{incident.get("title", "")} {incident.get("description", "")}".strip(),
            limit=3,
        )
    except Exception:
        knowledge_results = []

    knowledge_context = "\n\n".join(
        f"SOURCE {index}: {item.get("content", "")}"
        for index, item in enumerate(knowledge_results, start=1)
    )

    diagnosis_service = IncidentDiagnosisService(
        db
    )

    diagnosis = await diagnosis_service.diagnose(
        incident_id=incident["id"],
        title=incident.get(
            "title",
            "",
        ),
        description=incident.get(
            "description",
            "",
        ),
        service_name=incident.get(
            "service_name"
        ),
        environment=incident.get(
            "environment"
        ),
        created_by=state.get("user_id"),
        knowledge_context=knowledge_context,
        workflow_id=state.get("workflow_id"),
    )

    # ---------------------------------------------------------
    # ITSM RECOMMENDATION
    #
    # IMPORTANT:
    # AI ONLY RECOMMENDS.
    # It does NOT create an external ticket here.
    # ---------------------------------------------------------

    itsm_recommendation = diagnosis.get(
        "itsm_recommendation",
        {},
    )

    if not isinstance(
        itsm_recommendation,
        dict,
    ):
        itsm_recommendation = {}

    # ---------------------------------------------------------
    # BUILD ANSWER
    # ---------------------------------------------------------

    answer = diagnosis.get(
        "summary",
        "Incident diagnosis completed.",
    )

    if itsm_recommendation.get(
        "should_create_ticket",
        False,
    ):
        provider = itsm_recommendation.get(
            "provider",
            "none",
        )

        ticket_title = itsm_recommendation.get(
            "title",
            "",
        )

        answer += (
            "\n\nITSM Recommendation:\n"
            f"Provider: {provider}\n"
            f"Title: {ticket_title}\n"
            "Human approval is required "
            "before creating the ITSM ticket."
        )

    # ---------------------------------------------------------
    # RETURN UPDATED AGENT STATE
    # ---------------------------------------------------------

    return {
        **state,

        "answer": answer,

        "diagnosis": diagnosis,

        "itsm_recommendation": (
            itsm_recommendation
        ),

        "sources": [
            {
                "type": "incident",
                "incident_id": incident["id"],
                "tool": "get_incident",
            },
            *[
                {
                    "type": "document",
                    "document_id": item.get("document_id"),
                    "document_title": item.get("document_title"),
                    "chunk_id": item.get("chunk_id"),
                    "similarity": item.get("similarity"),
                }
                for item in knowledge_results
            ],
        ],
    }