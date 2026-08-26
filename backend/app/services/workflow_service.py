import json
import time
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_workflow import AgentWorkflow, AgentWorkflowStep, LLMUsage


class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start(self, *, user_id: int, question: str) -> AgentWorkflow:
        run = AgentWorkflow(
            workflow_id=f"WF-{uuid.uuid4().hex[:12].upper()}",
            user_id=user_id,
            question=question,
            status="RUNNING",
        )
        self.db.add(run)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def start_step(self, workflow_id: str, node_name: str, details: dict | None = None) -> AgentWorkflowStep:
        step = AgentWorkflowStep(
            workflow_id=workflow_id,
            node_name=node_name,
            status="RUNNING",
            details=json.dumps(details or {}, default=str),
        )
        self.db.add(step)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def finish_step(self, step_id: int, *, status: str = "SUCCESS", details: dict | None = None, error: str | None = None) -> None:
        step = await self.db.get(AgentWorkflowStep, step_id)
        if not step:
            return
        now = datetime.now(timezone.utc)
        step.completed_at = now
        if step.started_at:
            step.duration_ms = max(0.0, (now - step.started_at).total_seconds() * 1000)
        step.status = status
        if details is not None:
            step.details = json.dumps(details, default=str)
        step.error = error
        await self.db.commit()

    async def set_current_node(self, workflow_id: str, node_name: str, intent: str | None = None) -> None:
        run = await self.db.scalar(select(AgentWorkflow).where(AgentWorkflow.workflow_id == workflow_id))
        if not run:
            return
        run.current_node = node_name
        if intent:
            run.intent = intent
        await self.db.commit()

    async def finish(self, workflow_id: str, *, status: str, error: str | None = None) -> None:
        run = await self.db.scalar(select(AgentWorkflow).where(AgentWorkflow.workflow_id == workflow_id))
        if not run:
            return
        now = datetime.now(timezone.utc)
        run.status = status
        run.completed_at = now
        if run.started_at:
            run.duration_ms = max(0.0, (now - run.started_at).total_seconds() * 1000)
        run.error = error
        if status in {"COMPLETED", "FAILED", "WAITING_FOR_APPROVAL"}:
            run.current_node = None if status != "WAITING_FOR_APPROVAL" else "human_approval"
        await self.db.commit()

    async def record_llm_usage(self, *, workflow_id: str | None, user_id: int | None, agent_name: str | None, model_name: str, input_tokens: int, output_tokens: int, total_tokens: int, latency_ms: float, status: str = "SUCCESS") -> None:
        self.db.add(LLMUsage(
            workflow_id=workflow_id, user_id=user_id, agent_name=agent_name, model_name=model_name,
            input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total_tokens,
            latency_ms=latency_ms, status=status,
        ))
        await self.db.commit()

    async def workflow_detail(self, workflow_id: str) -> dict | None:
        run = await self.db.scalar(select(AgentWorkflow).where(AgentWorkflow.workflow_id == workflow_id))
        if not run:
            return None
        steps = list((await self.db.scalars(
            select(AgentWorkflowStep).where(AgentWorkflowStep.workflow_id == workflow_id).order_by(AgentWorkflowStep.id)
        )).all())
        usage = list((await self.db.scalars(
            select(LLMUsage).where(LLMUsage.workflow_id == workflow_id).order_by(LLMUsage.id)
        )).all())
        return {
            "workflow_id": run.workflow_id,
            "user_id": run.user_id,
            "question": run.question,
            "intent": run.intent,
            "status": run.status,
            "current_node": run.current_node,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "duration_ms": run.duration_ms,
            "error": run.error,
            "steps": [{
                "id": s.id, "node_name": s.node_name, "status": s.status,
                "started_at": s.started_at, "completed_at": s.completed_at,
                "duration_ms": s.duration_ms,
                "details": json.loads(s.details or "{}"),
                "error": s.error,
            } for s in steps],
            "llm_usage": [{
                "agent_name": u.agent_name, "model_name": u.model_name,
                "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                "total_tokens": u.total_tokens, "latency_ms": u.latency_ms,
                "status": u.status, "created_at": u.created_at,
            } for u in usage],
        }
