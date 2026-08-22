from app.db.base import Base
from app.db.database import engine

# Import models so SQLAlchemy registers them with Base.metadata.
from app.models.user import User  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
from app.models.incident import Incident  # noqa: F401
from app.models.incident_diagnosis import IncidentDiagnosis  # noqa: F401
from app.models.approval_request import ApprovalRequest  # noqa: F401
from app.models.audit_event import AuditEvent  # noqa: F401


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )