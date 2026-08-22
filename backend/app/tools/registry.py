from app.tools.base import BaseTool


class ToolRegistry:

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "requires_approval": tool.requires_approval,
            }
            for tool in self._tools.values()
        ]
