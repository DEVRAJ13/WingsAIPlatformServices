import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.tools.factory import build_tool_registry


class ToolExecutionService:
    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def execute_approved(
        self,
        *,
        approval_id: int,
        executed_by: int,
    ) -> dict[str, Any]:
        approval_service = ApprovalService(
            self.db
        )

        approval = await approval_service.repository.get(
            approval_id
        )

        # -----------------------------------------------------
        # APPROVAL EXISTENCE
        # -----------------------------------------------------

        if approval is None:
            raise ValueError(
                "Approval request not found."
            )

        # -----------------------------------------------------
        # PREVENT DUPLICATE EXECUTION
        # -----------------------------------------------------

        if approval.status == "EXECUTED":
            raise ValueError(
                "Approval request has already been executed."
            )

        # -----------------------------------------------------
        # ONLY APPROVED REQUESTS CAN EXECUTE
        # -----------------------------------------------------

        if approval.status != "APPROVED":
            raise ValueError(
                "Tool execution requires an APPROVED request."
            )

        # -----------------------------------------------------
        # TOOL REGISTRY
        # -----------------------------------------------------

        registry = build_tool_registry(
            self.db
        )

        tool = registry.get(
            approval.tool_name
        )

        if tool is None:
            raise ValueError(
                f"Tool '{approval.tool_name}' is not registered."
            )

        # -----------------------------------------------------
        # PARSE PARAMETERS
        # -----------------------------------------------------

        try:
            parameters = json.loads(
                approval.parameters
            )

        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "Approval request contains invalid tool parameters."
            ) from exc

        if not isinstance(parameters, dict):
            raise ValueError(
                "Tool parameters must be a JSON object."
            )

        # -----------------------------------------------------
        # EXECUTE TOOL
        # -----------------------------------------------------

        try:
            result = await tool.execute(
                **parameters
            )

        except Exception as exc:
            await self.db.rollback()

            raise RuntimeError(
                f"Tool '{approval.tool_name}' execution failed: "
                f"{str(exc)}"
            ) from exc

        # -----------------------------------------------------
        # VALIDATE TOOL RESULT
        # -----------------------------------------------------

        if not isinstance(result, dict):
            await self.db.rollback()

            raise ValueError(
                "Tool returned an invalid execution result."
            )

        # -----------------------------------------------------
        # TOOL FAILURE
        #
        # IMPORTANT:
        # Do NOT mark approval EXECUTED.
        # Preserve the actual provider error.
        # -----------------------------------------------------

        if not result.get("success", False):
            error_message = result.get(
                "message",
                "Tool execution failed.",
            )

            status_code = result.get(
                "status_code"
            )

            details = result.get(
                "details"
            )

            if status_code is not None:
                error_message = (
                    f"{error_message} "
                    f"HTTP status: {status_code}."
                )

            if details:
                error_message = (
                    f"{error_message} "
                    f"Details: {details}"
                )

            # -------------------------------------------------
            # AUDIT FAILED EXECUTION
            # -------------------------------------------------

            audit_service = AuditService(
                self.db
            )

            try:
                await audit_service.record(
                    event_type="TOOL_EXECUTION_FAILED",
                    user_id=executed_by,
                    tool_name=approval.tool_name,
                    approval_id=approval.id,
                    details={
                        "parameters": parameters,
                        "result": result,
                    },
                )

                await self.db.commit()

            except Exception:
                await self.db.rollback()

            raise ValueError(
                error_message
            )

        # -----------------------------------------------------
        # SUCCESSFUL TOOL EXECUTION
        # -----------------------------------------------------

        # Only now can the approval become EXECUTED.

        approval.status = "EXECUTED"

        # -----------------------------------------------------
        # AUDIT SUCCESSFUL EXECUTION
        # -----------------------------------------------------

        audit_service = AuditService(
            self.db
        )

        try:
            await audit_service.record(
                event_type="TOOL_EXECUTED",
                user_id=executed_by,
                tool_name=approval.tool_name,
                approval_id=approval.id,
                details={
                    "parameters": parameters,
                    "result": result,
                },
            )

            # -------------------------------------------------
            # COMMIT APPROVAL + AUDIT TOGETHER
            # -------------------------------------------------

            await self.db.commit()

        except Exception as exc:
            await self.db.rollback()

            raise RuntimeError(
                "Tool execution succeeded, but the "
                "execution transaction could not be committed."
            ) from exc

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {
            "approval_id": approval.id,
            "tool": approval.tool_name,
            "executed_by": executed_by,
            "status": approval.status,
            "result": result,
        }