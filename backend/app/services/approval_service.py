from app.core.rbac import can_approve
from app.repositories.approval_repository import ApprovalRepository
from app.services.audit_service import AuditService


class ApprovalService:
    def __init__(self, db):
        self.db = db
        self.repository = ApprovalRepository(db)
        self.audit_service = AuditService(db)

    async def request_approval(self, *, tool_name: str, requested_by: int, reason: str, parameters: dict, workflow_id: str | None = None) -> dict:
        approval = await self.repository.create(
            tool_name=tool_name,
            requested_by=requested_by,
            reason=reason,
            parameters=parameters,
            workflow_id=workflow_id,
        )
        await self.audit_service.record(
            event_type="APPROVAL_CREATED",
            user_id=requested_by,
            tool_name=tool_name,
            approval_id=approval.id,
            details={"reason": reason, "parameters": parameters},
        )
        await self.db.commit()
        return {
            "id": approval.id,
            "tool_name": approval.tool_name,
            "status": approval.status,
            "reason": approval.reason,
            "parameters": parameters,
            "workflow_id": approval.workflow_id,
        }

    async def decide(self, *, approval_id: int, decision: str, decision_by: int, decision_comment: str | None, decision_user=None) -> dict:
        if decision not in {"APPROVED", "REJECTED"}:
            raise ValueError("Decision must be APPROVED or REJECTED.")
        if decision_user is not None and not can_approve(decision_user):
            raise PermissionError("Your role is not authorized to approve operational actions.")
        approval = await self.repository.get(approval_id)
        if approval is None:
            raise ValueError("Approval request not found.")
        if approval.status != "PENDING":
            raise ValueError("Approval request has already been decided.")
        if approval.requested_by == decision_by:
            raise PermissionError("Separation of duties prevents a requester from approving their own request.")

        await self.repository.decide(
            approval=approval,
            decision=decision,
            decision_by=decision_by,
            decision_comment=decision_comment,
        )
        await self.audit_service.record(
            event_type="APPROVAL_APPROVED" if decision == "APPROVED" else "APPROVAL_REJECTED",
            user_id=decision_by,
            tool_name=approval.tool_name,
            approval_id=approval.id,
            details={"decision": decision, "comment": decision_comment, "workflow_id": approval.workflow_id},
        )
        if approval.workflow_id:
            from app.services.workflow_service import WorkflowService
            await WorkflowService(self.db).finish(
                approval.workflow_id,
                status="APPROVED" if decision == "APPROVED" else "REJECTED",
                error=None,
            )
        await self.db.commit()
        return {
            "id": approval.id,
            "tool_name": approval.tool_name,
            "status": approval.status,
            "decision_by": approval.decision_by,
            "decision_comment": approval.decision_comment,
        }
