from datetime import datetime

from pydantic import BaseModel, Field


class IncidentCreateRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = Field(
        min_length=1,
        max_length=20_000,
    )

    service_name: str | None = Field(
        default=None,
        max_length=255,
    )

    environment: str | None = Field(
        default=None,
        max_length=50,
    )


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    severity: str
    category: str | None
    service_name: str | None
    environment: str | None
    created_by: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }