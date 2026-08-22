from typing import Any

from app.itsm.base import ITSMProvider


class RemedyProvider(ITSMProvider):

    name = "remedy"

    async def create_ticket(
        self,
        *,
        title: str,
        description: str,
        priority: str,
        **kwargs: Any,
    ) -> dict:

        return {
            "success": False,
            "provider": self.name,
            "message": (
                "Remedy integration is not configured."
            ),
        }

    async def get_ticket(
        self,
        *,
        ticket_id: str,
        **kwargs: Any,
    ) -> dict:

        return {
            "success": False,
            "provider": self.name,
            "message": (
                "Remedy integration is not configured."
            ),
        }

    async def update_ticket(
        self,
        *,
        ticket_id: str,
        **fields: Any,
    ) -> dict:

        return {
            "success": False,
            "provider": self.name,
            "message": (
                "Remedy integration is not configured."
            ),
        }