import inspect
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph import END, START, StateGraph

from app.agents.incident_agent import incident_agent
from app.agents.itsm_agent import itsm_agent
from app.agents.knowledge_agent import knowledge_agent
from app.agents.state import AgentState
from app.agents.supervisor import supervisor
from app.core.rbac import can_execute
from app.services.approval_service import ApprovalService
from app.services.workflow_service import WorkflowService


logger = logging.getLogger(__name__)


def route_agent(state: AgentState) -> str:
    return state.get("intent", "knowledge")


def build_agent_graph(db: AsyncSession):
    workflow = WorkflowService(db)

    async def traced_node(state: AgentState, node_name: str, fn):
        workflow_id = state.get("workflow_id")
        step = await workflow.start_step(
            workflow_id,
            node_name,
            {"intent": state.get("intent"), "incident_id": state.get("incident_id")},
        )
        await workflow.set_current_node(workflow_id, node_name, state.get("intent"))
        try:
            result = fn(state)
            if inspect.isawaitable(result):
                result = await result
            await workflow.finish_step(
                step.id,
                status="SUCCESS",
                details={
                    "intent": result.get("intent"),
                    "approval_id": result.get("approval_id"),
                    "has_recommendation": bool(result.get("itsm_recommendation")),
                },
            )
            return result
        except Exception as exc:
            logger.exception(
                "Agent node failed: workflow_id=%s node=%s",
                workflow_id,
                node_name,
            )
            await workflow.finish_step(step.id, status="FAILED", error=str(exc))
            await workflow.finish(
                workflow_id,
                status="FAILED",
                error=str(exc),
            )
            raise

    async def supervisor_node(state: AgentState) -> AgentState:
        return await traced_node(
            state,
            "supervisor",
            lambda current: supervisor(current),
        )

    async def knowledge_node(state: AgentState) -> AgentState:
        return await traced_node(
            state,
            "knowledge_agent",
            lambda current: knowledge_agent(current, db),
        )

    async def incident_node(state: AgentState) -> AgentState:
        return await traced_node(
            state,
            "incident_agent",
            lambda current: incident_agent(current, db),
        )

    async def itsm_node(state: AgentState) -> AgentState:
        return await traced_node(
            state,
            "itsm_agent",
            lambda current: itsm_agent(current),
        )

    async def recommendation_node(state: AgentState) -> AgentState:
        async def execute(current):
            recommendation = current.get("itsm_recommendation") or {}
            if not recommendation.get("should_create_ticket"):
                return {**current, "answer": current.get("answer", ""), "next_node": "complete"}

            return {
                **current,
                "next_node": "approval_gate",
                "answer": (
                    current.get("answer", "")
                    + "\n\nRecommendation is ready for the WINGS approval workflow."
                ).strip(),
            }

        return await traced_node(state, "recommendation", execute)

    async def approval_gate_node(state: AgentState) -> AgentState:
        async def execute(current):
            recommendation = current.get("itsm_recommendation") or {}
            if not recommendation.get("should_create_ticket"):
                return {**current, "next_node": "complete"}

            approval_service = ApprovalService(db)
            approval = await approval_service.request_approval(
                tool_name="create_itsm_ticket",
                requested_by=current["user_id"],
                reason=(
                    f"AI recommendation: {recommendation.get('action', 'create ITSM ticket')}. "
                    "Human approval is required before external execution."
                ),
                workflow_id=current["workflow_id"],
                parameters={                    "provider": recommendation.get("provider", "jira"),
                    "title": recommendation.get("title", "WINGS AI recommended ITSM action"),
                    "description": recommendation.get("description", current.get("question", "")),
                    "priority": recommendation.get("priority", "MEDIUM"),
                },
            )
            return {
                **current,
                "approval_id": approval["id"],
                "next_node": "waiting_for_approval",
                "answer": (
                    current.get("answer", "")
                    + f"\n\nApproval request #{approval['id']} was created. "
                      "The external ITSM action has not been executed."
                ).strip(),
            }

        return await traced_node(state, "human_approval", execute)

    async def complete_node(state: AgentState) -> AgentState:
        return state

    async def waiting_node(state: AgentState) -> AgentState:
        return state

    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("incident", incident_node)
    graph.add_node("itsm", itsm_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("approval_gate", approval_gate_node)
    graph.add_node("complete", complete_node)
    graph.add_node("waiting_for_approval", waiting_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_agent,
        {"knowledge": "knowledge", "incident": "incident", "itsm": "itsm"},
    )

    graph.add_conditional_edges(
        "knowledge",
        lambda state: "complete",
        {"complete": "complete"},
    )
    graph.add_edge("incident", "recommendation")
    graph.add_edge("itsm", "recommendation")

    graph.add_conditional_edges(
        "recommendation",
        lambda state: "approval_gate" if state.get("next_node") == "approval_gate" else "complete",
        {"approval_gate": "approval_gate", "complete": "complete"},
    )
    graph.add_conditional_edges(
        "approval_gate",
        lambda state: "waiting_for_approval" if state.get("next_node") == "waiting_for_approval" else "complete",
        {"waiting_for_approval": "waiting_for_approval", "complete": "complete"},
    )

    graph.add_edge("complete", END)
    graph.add_edge("waiting_for_approval", END)

    return graph.compile()
