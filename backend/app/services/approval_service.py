from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.approval_repository import (
    ApprovalRepository,
)
from app.services.audit_service import AuditService


class ApprovalService:

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db
        self.repository = ApprovalRepository(
            db
        )
        self.audit_service = AuditService(
            db
        )

    async def request_approval(
        self,
        *,
        tool_name: str,
        requested_by: int,
        reason: str,
        parameters: dict,
    ) -> dict:

        # -----------------------------------------------------
        # CREATE APPROVAL
        # -----------------------------------------------------

        approval = await self.repository.create(
            tool_name=tool_name,
            requested_by=requested_by,
            reason=reason,
            parameters=parameters,
        )

        # -----------------------------------------------------
        # AUDIT APPROVAL CREATION
        # -----------------------------------------------------

        await self.audit_service.record(
            event_type="APPROVAL_CREATED",
            user_id=requested_by,
            tool_name=tool_name,
            approval_id=approval.id,
            details={
                "reason": reason,
                "parameters": parameters,
            },
        )

        # -----------------------------------------------------
        # COMMIT APPROVAL + AUDIT EVENT TOGETHER
        # -----------------------------------------------------

        await self.db.commit()

        return {
            "id": approval.id,
            "tool_name": approval.tool_name,
            "status": approval.status,
            "reason": approval.reason,
            "parameters": parameters,
        }

    async def decide(
        self,
        *,
        approval_id: int,
        decision: str,
        decision_by: int,
        decision_comment: str | None,
    ) -> dict:

        # -----------------------------------------------------
        # VALIDATE DECISION
        # -----------------------------------------------------

        if decision not in {
            "APPROVED",
            "REJECTED",
        }:
            raise ValueError(
                "Decision must be APPROVED or REJECTED."
            )

        # -----------------------------------------------------
        # GET APPROVAL
        # -----------------------------------------------------

        approval = await self.repository.get(
            approval_id
        )

        if approval is None:
            raise ValueError(
                "Approval request not found."
            )

        # -----------------------------------------------------
        # PREVENT SECOND DECISION
        # -----------------------------------------------------

        if approval.status != "PENDING":
            raise ValueError(
                "Approval request has already been decided."
            )

        # -----------------------------------------------------
        # UPDATE APPROVAL
        # -----------------------------------------------------

        await self.repository.decide(
            approval=approval,
            decision=decision,
            decision_by=decision_by,
            decision_comment=decision_comment,
        )

        # -----------------------------------------------------
        # AUDIT DECISION
        # -----------------------------------------------------

        event_type = (
            "APPROVAL_APPROVED"
            if decision == "APPROVED"
            else "APPROVAL_REJECTED"
        )

        await self.audit_service.record(
            event_type=event_type,
            user_id=decision_by,
            tool_name=approval.tool_name,
            approval_id=approval.id,
            details={
                "decision": decision,
                "comment": decision_comment,
            },
        )

        # -----------------------------------------------------
        # COMMIT APPROVAL + AUDIT EVENT TOGETHER
        # -----------------------------------------------------

        await self.db.commit()

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {
            "id": approval.id,
            "tool_name": approval.tool_name,
            "status": approval.status,
            "decision_by": approval.decision_by,
            "decision_comment": approval.decision_comment,
        }