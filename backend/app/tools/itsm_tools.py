from typing import Any

from app.services.itsm_service import ITSMService
from app.tools.base import BaseTool


class CreateITSMTicketTool(BaseTool):

    name = "create_itsm_ticket"

    description = (
        "Create an incident or service ticket "
        "in an enterprise ITSM platform."
    )

    requires_approval = True

    def __init__(self) -> None:
        self.itsm_service = ITSMService()

    async def execute(
        self,
        *,
        provider: str,
        title: str,
        description: str,
        priority: str,
        **kwargs: Any,
    ) -> dict:

        return await self.itsm_service.create_ticket(
            provider=provider,
            title=title,
            description=description,
            priority=priority,
            **kwargs,
        )