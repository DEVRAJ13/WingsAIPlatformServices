from pydantic import BaseModel


class IncidentDiagnosis(BaseModel):
    severity: str
    category: str
    summary: str
    likely_causes: list[str]
    recommended_actions: list[str]
    requires_human_approval: bool