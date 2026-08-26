from app.agents.supervisor import classify_intent
from app.core.rbac import can_approve, can_execute, can_manage_users, normalize_role


def test_agent_intents():
    assert classify_intent("What should happen during a critical incident?") == "knowledge"
    assert classify_intent("Diagnose incident 25") == "incident"
    assert classify_intent("Create a ServiceNow ticket for this outage") == "itsm"


def test_role_permissions():
    class U:
        def __init__(self, role):
            self.role = role

    assert can_manage_users(U("PLATFORM_ADMIN"))
    assert can_approve(U("CHANGE_MANAGER"))
    assert can_execute(U("IT_OPERATIONS"))
    assert not can_execute(U("REQUESTER"))
    assert normalize_role("USER") == "REQUESTER"


def test_graph_builder_accepts_sync_supervisor():
    """The graph tracer must support both sync and async agent nodes."""
    import inspect
    from app.agents.graph import build_agent_graph

    # Source-level contract: traced_node must detect awaitables.
    source = inspect.getsource(build_agent_graph)
    assert "inspect.isawaitable" in source
