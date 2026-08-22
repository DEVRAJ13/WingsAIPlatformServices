from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.incident_agent import incident_agent
from app.agents.itsm_agent import itsm_agent
from app.agents.knowledge_agent import knowledge_agent
from app.agents.state import AgentState
from app.agents.supervisor import supervisor


def route_agent(state: AgentState) -> str:
    intent = state.get("intent", "knowledge")

    if intent == "incident":
        return "incident"

    if intent == "itsm":
        return "itsm"

    return "knowledge"


def build_agent_graph(db: AsyncSession):

    async def knowledge_node(
        state: AgentState,
    ) -> AgentState:
        return await knowledge_agent(
            state,
            db,
        )

    async def incident_node(
        state: AgentState,
    ) -> AgentState:
        return await incident_agent(
            state,
            db,
        )

    async def itsm_node(
        state: AgentState,
    ) -> AgentState:
        return await itsm_agent(
            state,
        )

    graph = StateGraph(AgentState)

    # Supervisor
    graph.add_node(
        "supervisor",
        supervisor,
    )

    # Agents
    graph.add_node(
        "knowledge",
        knowledge_node,
    )

    graph.add_node(
        "incident",
        incident_node,
    )

    graph.add_node(
        "itsm",
        itsm_node,
    )

    # START → Supervisor
    graph.add_edge(
        START,
        "supervisor",
    )

    # Supervisor → Agent
    graph.add_conditional_edges(
        "supervisor",
        route_agent,
        {
            "knowledge": "knowledge",
            "incident": "incident",
            "itsm": "itsm",
        },
    )

    # Agents → END
    graph.add_edge(
        "knowledge",
        END,
    )

    graph.add_edge(
        "incident",
        END,
    )

    graph.add_edge(
        "itsm",
        END,
    )

    return graph.compile()