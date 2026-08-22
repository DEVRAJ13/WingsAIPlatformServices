import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_diagnosis import IncidentDiagnosis


class IncidentDiagnosisRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        incident_id: int,
        severity: str,
        category: str,
        summary: str,
        likely_causes: list[str],
        recommended_actions: list[str],
        requires_human_approval: bool,
        model_name: str,
        created_by: int | None,
    ) -> IncidentDiagnosis:

        diagnosis = IncidentDiagnosis(
            incident_id=incident_id,
            severity=severity,
            category=category,
            summary=summary,
            likely_causes=json.dumps(likely_causes),
            recommended_actions=json.dumps(
                recommended_actions
            ),
            requires_human_approval=requires_human_approval,
            model_name=model_name,
            created_by=created_by,
        )

        self.db.add(diagnosis)

        await self.db.flush()

        return diagnosis

    async def list_by_incident(
        self,
        incident_id: int,
    ) -> list[IncidentDiagnosis]:

        result = await self.db.execute(
            select(IncidentDiagnosis)
            .where(
                IncidentDiagnosis.incident_id == incident_id
            )
            .order_by(
                IncidentDiagnosis.created_at.desc()
            )
        )

        return list(result.scalars().all())