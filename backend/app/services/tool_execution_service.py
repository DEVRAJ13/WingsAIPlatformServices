import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.tools.factory import build_tool_registry


class ToolExecutionService:
    """Execute an already-approved tool without corrupting the approval state."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def execute_approved(
        self,
        *,
        approval_id: int,
        executed_by: int,
    ) -> dict[str, Any]:
        approval_service = ApprovalService(self.db)
        approval = await approval_service.repository.get(approval_id)

        if approval is None:
            raise ValueError("Approval request not found.")

        # Copy values before any external call/rollback. SQLAlchemy may
        # expire ORM attributes after rollback.
        approval_tool_name = approval.tool_name
        approval_status = approval.status

        if approval_status == "EXECUTED":
            raise ValueError("Approval request has already been executed.")

        if approval_status != "APPROVED":
            raise ValueError("Tool execution requires an APPROVED request.")

        registry = build_tool_registry(self.db)
        tool = registry.get(approval_tool_name)

        if tool is None:
            raise ValueError(
                f"Tool '{approval_tool_name}' is not registered."
            )

        try:
            parameters = json.loads(approval.parameters)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "Approval request contains invalid tool parameters."
            ) from exc

        if not isinstance(parameters, dict):
            raise ValueError("Tool parameters must be a JSON object.")

        # Existing approvals created before the Jira provider became
        # optional may not contain provider. Preserve backward compatibility.
        if approval_tool_name == "create_itsm_ticket":
            parameters.setdefault("provider", "jira")

        try:
            result = await tool.execute(**parameters)
        except Exception as exc:
            # Rollback only our DB transaction. Do not touch ORM attributes
            # after rollback; they may require an implicit DB load.
            await self.db.rollback()

            # Record a stable error using local immutable values.
            raise RuntimeError(
                f"Tool '{approval_tool_name}' execution failed: {exc}"
            ) from exc

        if not isinstance(result, dict):
            await self.db.rollback()
            raise ValueError("Tool returned an invalid execution result.")

        if not result.get("success", False):
            error_message = result.get("message", "Tool execution failed.")
            status_code = result.get("status_code")
            details = result.get("details")

            if status_code is not None:
                error_message = (
                    f"{error_message} HTTP status: {status_code}."
                )
            if details:
                error_message = f"{error_message} Details: {details}"

            # The provider call itself should not be allowed to mark the
            # approval EXECUTED. Audit the failure where possible.
            try:
                await self.db.rollback()
                await AuditService(self.db).record(
                    event_type="TOOL_EXECUTION_FAILED",
                    user_id=executed_by,
                    tool_name=approval_tool_name,
                    approval_id=approval_id,
                    details={
                        "parameters": parameters,
                        "result": result,
                    },
                )
                await self.db.commit()
            except Exception:
                await self.db.rollback()

            raise ValueError(error_message)

        # Mark EXECUTED only after the provider confirms success.
        approval.status = "EXECUTED"

        try:
            await AuditService(self.db).record(
                event_type="TOOL_EXECUTED",
                user_id=executed_by,
                tool_name=approval_tool_name,
                approval_id=approval_id,
                details={
                    "parameters": parameters,
                    "result": result,
                },
            )
            await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            raise RuntimeError(
                "Tool execution succeeded, but the execution transaction "
                "could not be committed."
            ) from exc

        return {
            "approval_id": approval_id,
            "tool": approval_tool_name,
            "executed_by": executed_by,
            "status": "EXECUTED",
            "result": result,
        }
