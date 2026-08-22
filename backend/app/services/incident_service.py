from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.incident_repository import (
    IncidentRepository,
)


class IncidentService:

    def __init__(self, db: AsyncSession) -> None:
        self.repository = IncidentRepository(db)
        self.db = db

    async def create_incident(
        self,
        *,
        title: str,
        description: str,
        service_name: str | None,
        environment: str | None,
        created_by: int | None,
    ):

        incident = await self.repository.create(
            title=title,
            description=description,
            service_name=service_name,
            environment=environment,
            created_by=created_by,
        )

        await self.db.commit()

        await self.db.refresh(incident)

        return incident

    async def get_incident(
        self,
        incident_id: int,
    ):

        return await self.repository.get_by_id(
            incident_id
        )