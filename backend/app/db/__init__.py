from app.db.base import Base
from app.db.database import engine

# Import models so SQLAlchemy registers them with Base.metadata.
from app.models.user import User  # noqa: F401


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )