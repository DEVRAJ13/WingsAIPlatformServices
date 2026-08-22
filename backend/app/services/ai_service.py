from app.ai.gateway import AIGateway


class AIService:
    def __init__(self) -> None:
        self.gateway = AIGateway()

    async def chat(
        self,
        message: str,
    ) -> str:
        return await self.gateway.generate(message)