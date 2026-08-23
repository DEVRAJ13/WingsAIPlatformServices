from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.schemas.incident import (
    IncidentCreateRequest,
    IncidentResponse,
)
from app.services.incident_service import IncidentService
from app.models.incident import Incident


router = APIRouter()


@router.get("")
async def list_incidents(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[IncidentResponse]:
    result = await db.execute(
        select(Incident).order_by(Incident.id.desc()).limit(100)
    )
    return list(result.scalars().all())


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    request: IncidentCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:

    service = IncidentService(db)

    incident = await service.create_incident(
        title=request.title,
        description=request.description,
        service_name=request.service_name,
        environment=request.environment,
        created_by=current_user.id,
    )

    return incident


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_incident(
    incident_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:

    service = IncidentService(db)

    incident = await service.get_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found.",
        )

    return incident