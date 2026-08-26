import json
import asyncio
import time
import httpx
from sqlalchemy import func, select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import require_roles, get_db
from app.models.agent_workflow import AgentWorkflow, AgentWorkflowStep, LLMUsage
from app.models.audit_event import AuditEvent

router = APIRouter()


def _health(name, status="HEALTHY", latency_ms=None, message=""):
    return {"name": name, "status": status, "latency_ms": latency_ms, "message": message}


@router.get("/health")
async def monitoring_health(
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR")),
    db: AsyncSession = Depends(get_db),
):
    from app.core.config import settings

    async def probe_ollama():
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
                response.raise_for_status()
            return _health("Ollama", "HEALTHY", (time.perf_counter() - started) * 1000)
        except Exception as exc:
            return _health("Ollama", "DOWN", (time.perf_counter() - started) * 1000, str(exc))

    async def probe_jira():
        if not all([settings.jira_base_url, settings.jira_email, settings.jira_api_token]):
            return _health("Jira", "NOT_CONFIGURED", message="Jira credentials are not configured.")
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{settings.jira_base_url.rstrip('/')}/rest/api/3/myself",
                    auth=(settings.jira_email, settings.jira_api_token),
                    headers={"Accept": "application/json"},
                )
            status = "HEALTHY" if response.status_code < 400 else "DOWN"
            return _health("Jira", status, (time.perf_counter() - started) * 1000, "" if status == "HEALTHY" else f"HTTP {response.status_code}")
        except Exception as exc:
            return _health("Jira", "DOWN", (time.perf_counter() - started) * 1000, str(exc))

    async def probe_servicenow():
        if not all([settings.servicenow_base_url, settings.servicenow_username, settings.servicenow_password]):
            return _health("ServiceNow", "NOT_CONFIGURED", message="ServiceNow credentials are not configured.")
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{settings.servicenow_base_url.rstrip('/')}/api/now/table/incident",
                    params={"sysparm_limit": "1"},
                    auth=(settings.servicenow_username, settings.servicenow_password),
                    headers={"Accept": "application/json"},
                )
            status = "HEALTHY" if response.status_code < 400 else "DOWN"
            return _health("ServiceNow", status, (time.perf_counter() - started) * 1000, "" if status == "HEALTHY" else f"HTTP {response.status_code}")
        except Exception as exc:
            return _health("ServiceNow", "DOWN", (time.perf_counter() - started) * 1000, str(exc))

    import time
    started = time.perf_counter()
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_status = _health("PostgreSQL", "HEALTHY", (time.perf_counter() - started) * 1000)
    except Exception as exc:
        db_status = _health("PostgreSQL", "DOWN", (time.perf_counter() - started) * 1000, str(exc))

    services = await asyncio.gather(probe_ollama(), probe_jira(), probe_servicenow())
    return {
        "services": [
            db_status,
            _health("FastAPI Backend"),
            _health("pgvector"),
            *services,
        ]
    }


@router.get("/overview")
async def monitoring_overview(
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR")),
    db: AsyncSession = Depends(get_db),
):
    total_runs = await db.scalar(select(func.count(AgentWorkflow.id))) or 0
    completed = await db.scalar(select(func.count(AgentWorkflow.id)).where(AgentWorkflow.status == "COMPLETED")) or 0
    failed = await db.scalar(select(func.count(AgentWorkflow.id)).where(AgentWorkflow.status == "FAILED")) or 0
    running = await db.scalar(select(func.count(AgentWorkflow.id)).where(AgentWorkflow.status == "RUNNING")) or 0
    waiting = await db.scalar(select(func.count(AgentWorkflow.id)).where(AgentWorkflow.status == "WAITING_FOR_APPROVAL")) or 0

    input_tokens = await db.scalar(select(func.coalesce(func.sum(LLMUsage.input_tokens), 0))) or 0
    output_tokens = await db.scalar(select(func.coalesce(func.sum(LLMUsage.output_tokens), 0))) or 0
    total_tokens = await db.scalar(select(func.coalesce(func.sum(LLMUsage.total_tokens), 0))) or 0
    avg_latency = await db.scalar(select(func.avg(LLMUsage.latency_ms)))

    return {
        "workflows": {
            "total": total_runs,
            "completed": completed,
            "failed": failed,
            "running": running,
            "waiting_for_approval": waiting,
            "success_rate": round((completed / total_runs) * 100, 2) if total_runs else 0,
        },
        "llm": {
            "requests": await db.scalar(select(func.count(LLMUsage.id))) or 0,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "total_tokens": int(total_tokens),
            "avg_latency_ms": round(float(avg_latency), 2) if avg_latency is not None else 0,
        },
    }


@router.get("/agents")
async def monitoring_agents(
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR")),
    db: AsyncSession = Depends(get_db),
):
    step_rows = (await db.execute(
        select(
            AgentWorkflowStep.node_name,
            func.count(AgentWorkflowStep.id).label("requests"),
            func.sum(
                (AgentWorkflowStep.status == "FAILED").cast(__import__("sqlalchemy").Integer)
            ).label("failures"),
        )
        .group_by(AgentWorkflowStep.node_name)
    )).all()

    usage_rows = (await db.execute(
        select(
            LLMUsage.agent_name,
            func.count(LLMUsage.id).label("llm_requests"),
            func.sum(LLMUsage.input_tokens).label("input_tokens"),
            func.sum(LLMUsage.output_tokens).label("output_tokens"),
            func.sum(LLMUsage.total_tokens).label("total_tokens"),
            func.avg(LLMUsage.latency_ms).label("avg_latency_ms"),
        )
        .group_by(LLMUsage.agent_name)
    )).all()

    names = [
        "supervisor",
        "knowledge_agent",
        "incident_agent",
        "itsm_agent",
        "recommendation",
        "human_approval",
        "execution",
        "verification",
    ]
    step_map = {r.node_name: r for r in step_rows}
    usage_map = {r.agent_name: r for r in usage_rows}

    results = []
    for name in names:
        step = step_map.get(name)
        usage = usage_map.get(name)
        requests = int(step.requests or 0) if step else int(usage.llm_requests or 0) if usage else 0
        failures = int(step.failures or 0) if step else 0
        results.append({
            "agent_name": name,
            "status": "DEGRADED" if failures else "HEALTHY",
            "requests": requests,
            "failures": failures,
            "input_tokens": int(usage.input_tokens or 0) if usage else 0,
            "output_tokens": int(usage.output_tokens or 0) if usage else 0,
            "total_tokens": int(usage.total_tokens or 0) if usage else 0,
            "avg_latency_ms": round(float(usage.avg_latency_ms or 0), 2) if usage else 0,
        })
    return {"agents": results}


@router.get("/workflows")
async def monitoring_workflows(
    limit: int = 50,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR")),
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    runs = list((await db.scalars(select(AgentWorkflow).order_by(AgentWorkflow.id.desc()).limit(limit))).all())
    return {"workflows": [{
        "workflow_id": r.workflow_id,
        "user_id": r.user_id,
        "question": r.question,
        "intent": r.intent,
        "status": r.status,
        "current_node": r.current_node,
        "started_at": r.started_at,
        "completed_at": r.completed_at,
        "duration_ms": r.duration_ms,
        "error": r.error,
    } for r in runs]}


@router.get("/workflows/{workflow_id}")
async def monitoring_workflow_detail(
    workflow_id: str,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN", "IT_MANAGER", "AUDITOR")),
    db: AsyncSession = Depends(get_db),
):
    from app.services.workflow_service import WorkflowService
    detail = await WorkflowService(db).workflow_detail(workflow_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return detail


@router.get("/audit")
async def monitoring_audit(
    limit: int = 100,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN", "AUDITOR")),
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 300))
    rows = list((await db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit))).all())
    return {"events": [{
        "id": e.id,
        "event_type": e.event_type,
        "user_id": e.user_id,
        "tool_name": e.tool_name,
        "approval_id": e.approval_id,
        "entity_type": e.entity_type,
        "entity_id": e.entity_id,
        "details": json.loads(e.details or "{}"),
        "created_at": e.created_at,
    } for e in rows]}
