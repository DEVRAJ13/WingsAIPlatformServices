from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


bearer_scheme = HTTPBearer(auto_error=True)


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    repository = UserRepository(db)

    return UserService(repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_access_token(
            credentials.credentials
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repository = UserRepository(db)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user