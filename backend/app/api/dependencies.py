from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    repository = UserRepository(db)

    return UserService(repository)