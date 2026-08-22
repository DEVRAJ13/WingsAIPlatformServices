import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


class AuditRepository:

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def create(
        self,
        *,
        event_type: str,
        user_id: int | None = None,
        tool_name: str | None = None,
        approval_id: int | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        details: dict | None = None,
    ) -> AuditEvent:

        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            tool_name=tool_name,
            approval_id=approval_id,
            entity_type=entity_type,
            entity_id=entity_id,
            details=(
                json.dumps(details)
                if details is not None
                else None
            ),
        )

        self.db.add(event)

        await self.db.flush()

        return event

    async def get_by_entity(
        self,
        *,
        entity_type: str,
        entity_id: int,
    ) -> list[AuditEvent]:

        result = await self.db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id,
            )
            .order_by(
                AuditEvent.created_at.asc()
            )
        )

        return list(result.scalars().all())