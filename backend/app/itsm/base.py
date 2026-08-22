from abc import ABC, abstractmethod
from typing import Any


class ITSMProvider(ABC):

    name: str

    @abstractmethod
    async def create_ticket(
        self,
        *,
        title: str,
        description: str,
        priority: str,
        **kwargs: Any,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_ticket(
        self,
        *,
        ticket_id: str,
        **kwargs: Any,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def update_ticket(
        self,
        *,
        ticket_id: str,
        **fields: Any,
    ) -> dict:
        raise NotImplementedError