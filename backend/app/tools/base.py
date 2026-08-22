from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):

    name: str
    description: str
    requires_approval: bool = True

    @abstractmethod
    async def execute(
        self,
        **kwargs: Any,
    ) -> dict:
        raise NotImplementedError
