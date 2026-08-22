from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.incident_service import IncidentService
from app.tools.base import BaseTool


class GetIncidentTool(BaseTool):

    name = "get_incident"

    description = (
        "Retrieve incident details by incident ID."
    )

    # Reading data does not require approval.
    requires_approval = False

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def execute(
        self,
        *,
        incident_id: int,
        **kwargs: Any,
    ) -> dict:

        service = IncidentService(self.db)

        incident = await service.get_incident(
            incident_id
        )

        if incident is None:
            return {
                "success": False,
                "message": "Incident not found.",
            }

        return {
            "success": True,
            "incident": {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "status": incident.status,
                "severity": incident.severity,
                "service_name": incident.service_name,
                "environment": incident.environment,
            },
        }


class UpdateIncidentTool(BaseTool):

    name = "update_incident"

    description = (
        "Update an incident status, severity, or description."
    )

    requires_approval = True

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def execute(
        self,
        *,
        incident_id: int,
        status: str | None = None,
        severity: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> dict:

        service = IncidentService(self.db)

        incident = await service.get_incident(
            incident_id
        )

        if incident is None:
            return {
                "success": False,
                "message": "Incident not found.",
            }

        if status is not None:
            incident.status = status

        if severity is not None:
            incident.severity = severity

        if description is not None:
            incident.description = description

        await self.db.commit()

        return {
            "success": True,
            "message": "Incident updated successfully.",
            "incident": {
                "id": incident.id,
                "status": incident.status,
                "severity": incident.severity,
                "description": incident.description,
            },
        }