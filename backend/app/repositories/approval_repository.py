import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_request import ApprovalRequest


class ApprovalRepository:

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def create(
        self,
        *,
        tool_name: str,
        requested_by: int,
        reason: str,
        parameters: dict,
    ) -> ApprovalRequest:

        approval = ApprovalRequest(
            tool_name=tool_name,
            requested_by=requested_by,
            status="PENDING",
            reason=reason,
            parameters=json.dumps(parameters),
        )

        self.db.add(approval)

        await self.db.flush()

        return approval

    async def get(
        self,
        approval_id: int,
    ) -> ApprovalRequest | None:

        result = await self.db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == approval_id
            )
        )

        return result.scalar_one_or_none()

    async def decide(
        self,
        *,
        approval: ApprovalRequest,
        decision: str,
        decision_by: int,
        decision_comment: str | None,
    ) -> ApprovalRequest:

        approval.status = decision
        approval.decision_by = decision_by
        approval.decision_comment = decision_comment
        approval.decided_at = datetime.now(timezone.utc)

        await self.db.flush()

        return approval