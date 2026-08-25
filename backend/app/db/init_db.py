from sqlalchemy import text
from app.db.base import Base
from app.db.database import engine
from app.core.config import settings
from app.models.user import User  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
from app.models.incident import Incident  # noqa: F401
from app.models.incident_diagnosis import IncidentDiagnosis  # noqa: F401
from app.models.approval_request import ApprovalRequest  # noqa: F401
from app.models.audit_event import AuditEvent  # noqa: F401


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_id VARCHAR(100)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(150)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS designation VARCHAR(150)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS manager_name VARCHAR(150)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE'",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE users ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP",
        ]
        for statement in migrations:
            await connection.execute(text(statement))
        await connection.execute(text("UPDATE users SET status='ACTIVE' WHERE status IS NULL"))
        await connection.execute(text("UPDATE users SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL"))

        email = getattr(settings, "rbac_bootstrap_admin_email", None)
        if email:
            await connection.execute(
                text("UPDATE users SET role='PLATFORM_ADMIN', status='ACTIVE' WHERE lower(email)=lower(:email)"),
                {"email": email},
            )
