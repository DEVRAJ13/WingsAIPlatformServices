from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident


class IncidentRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        title: str,
        description: str,
        service_name: str | None,
        environment: str | None,
        created_by: int | None,
    ) -> Incident:

        incident = Incident(
            title=title,
            description=description,
            service_name=service_name,
            environment=environment,
            created_by=created_by,
        )

        self.db.add(incident)

        await self.db.flush()

        return incident

    async def get_by_id(
        self,
        incident_id: int,
    ) -> Incident | None:

        result = await self.db.execute(
            select(Incident).where(
                Incident.id == incident_id
            )
        )

        return result.scalar_one_or_none()