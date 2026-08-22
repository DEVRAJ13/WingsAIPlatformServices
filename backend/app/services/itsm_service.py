from typing import Any

from app.itsm.factory import get_itsm_provider


class ITSMService:

    async def create_ticket(
        self,
        *,
        provider: str,
        title: str,
        description: str,
        priority: str,
        **kwargs: Any,
    ) -> dict:

        itsm_provider = get_itsm_provider(
            provider
        )

        return await itsm_provider.create_ticket(
            title=title,
            description=description,
            priority=priority,
            **kwargs,
        )

    async def get_ticket(
        self,
        *,
        provider: str,
        ticket_id: str,
        **kwargs: Any,
    ) -> dict:

        itsm_provider = get_itsm_provider(
            provider
        )

        return await itsm_provider.get_ticket(
            ticket_id=ticket_id,
            **kwargs,
        )

    async def update_ticket(
        self,
        *,
        provider: str,
        ticket_id: str,
        **fields: Any,
    ) -> dict:

        itsm_provider = get_itsm_provider(
            provider
        )

        return await itsm_provider.update_ticket(
            ticket_id=ticket_id,
            **fields,
        )