from app.services.itsm_service import ITSMService
from app.tools.base import BaseTool


class GetITSMTicketTool(BaseTool):

    name = "get_itsm_ticket"

    description = (
        "Retrieve an existing ITSM ticket."
    )

    # Read-only operation.
    requires_approval = False

    def __init__(self) -> None:
        self.itsm_service = ITSMService()

    async def execute(
        self,
        *,
        provider: str,
        ticket_id: str,
    ) -> dict:

        return await self.itsm_service.get_ticket(
            provider=provider,
            ticket_id=ticket_id,
        )