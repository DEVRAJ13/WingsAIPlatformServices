import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.incident_diagnosis_repository import (
    IncidentDiagnosisRepository,
)
from app.services.llm_service import LLMService


class IncidentDiagnosisService:

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.llm = LLMService()

        self.repository = IncidentDiagnosisRepository(
            db
        )

        self.db = db

    async def diagnose(
        self,
        *,
        incident_id: int,
        title: str,
        description: str,
        service_name: str | None,
        environment: str | None,
        created_by: int | None,
    ) -> dict:

        prompt = f"""
You are the WINGS Enterprise Incident Diagnosis Agent.

Analyze the incident and return ONLY valid JSON.

Required JSON structure:

{{
  "severity": "LOW|MEDIUM|HIGH|CRITICAL|UNKNOWN",
  "category": "APPLICATION|DATABASE|NETWORK|INFRASTRUCTURE|SECURITY|UNKNOWN",
  "summary": "short summary",

  "likely_causes": [
    "cause 1",
    "cause 2"
  ],

  "recommended_actions": [
    "action 1",
    "action 2"
  ],

  "requires_human_approval": true,

  "itsm_recommendation": {{
    "should_create_ticket": true,
    "provider": "jira|servicenow|remedy|none",
    "title": "ticket title",
    "description": "ticket description",
    "priority": "LOW|MEDIUM|HIGH|CRITICAL"
  }}
}}

Rules:

- Do not invent facts.
- Base the analysis only on the incident information supplied.
- Do not claim that an action was performed.
- Never create or approve an external ITSM ticket.
- Creating an ITSM ticket always requires human approval.
- If there is insufficient information, use UNKNOWN.
- If an ITSM ticket is not appropriate, use:
  "should_create_ticket": false
  and
  "provider": "none".

INCIDENT TITLE:
{title}

DESCRIPTION:
{description}

SERVICE:
{service_name or "UNKNOWN"}

ENVIRONMENT:
{environment or "UNKNOWN"}
"""
        raw_response = await self.llm.generate(prompt)

        try:
            result = json.loads(raw_response)

        except json.JSONDecodeError:
            result = {
                "severity": "UNKNOWN",
                "category": "UNKNOWN",
                "summary": raw_response[:1000],
                "likely_causes": [],
                "recommended_actions": [],
                "requires_human_approval": True,
            }

        diagnosis = {
            "severity": result.get(
                "severity",
                "UNKNOWN",
            ),
            "category": result.get(
                "category",
                "UNKNOWN",
            ),
            "summary": result.get(
                "summary",
                "",
            ),
            "likely_causes": result.get(
                "likely_causes",
                [],
            ),
            "recommended_actions": result.get(
                "recommended_actions",
                [],
            ),
            "requires_human_approval": result.get(
                "requires_human_approval",
                True,
            ),
        }

        # Persist AI diagnosis for audit/history.
        await self.repository.create(
            incident_id=incident_id,
            severity=diagnosis["severity"],
            category=diagnosis["category"],
            summary=diagnosis["summary"],
            likely_causes=diagnosis["likely_causes"],
            recommended_actions=diagnosis[
                "recommended_actions"
            ],
            requires_human_approval=diagnosis[
                "requires_human_approval"
            ],
            model_name=settings.ollama_model,
            created_by=created_by,
        )

        await self.db.commit()

        return diagnosis