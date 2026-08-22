from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_repository import (
    AuditRepository,
)


class AuditService:

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.repository = AuditRepository(db)

    async def record(
        self,
        *,
        event_type: str,
        user_id: int | None = None,
        tool_name: str | None = None,
        approval_id: int | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        details: dict | None = None,
    ) -> dict:

        event = await self.repository.create(
            event_type=event_type,
            user_id=user_id,
            tool_name=tool_name,
            approval_id=approval_id,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )

        return {
            "id": event.id,
            "event_type": event.event_type,
            "user_id": event.user_id,
            "tool_name": event.tool_name,
            "approval_id": event.approval_id,
        }