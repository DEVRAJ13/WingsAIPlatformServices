from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.incident_tools import (
    GetIncidentTool,
    UpdateIncidentTool,
)
from app.tools.itsm_tools import (
    CreateITSMTicketTool,
)
from app.tools.registry import ToolRegistry
from app.tools.itsm_tools import CreateITSMTicketTool
from app.tools.itsm_read_tools import GetITSMTicketTool


def build_tool_registry(
    db: AsyncSession,
) -> ToolRegistry:

    registry = ToolRegistry()

    registry.register(
        GetIncidentTool(db)
    )

    registry.register(
        UpdateIncidentTool(db)
    )

    registry.register(
        CreateITSMTicketTool()
    )

    registry.register(
        GetITSMTicketTool()
    )

    return registry