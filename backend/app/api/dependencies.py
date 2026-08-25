from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rbac import normalize_role
from app.core.security import decode_access_token
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=True)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"}) from exc
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid user ID in access token", headers={"WWW-Authenticate": "Bearer"}) from exc
    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    if payload.get("token_version", 0) != user.token_version:
        raise HTTPException(status_code=401, detail="Access token has been invalidated. Please sign in again.", headers={"WWW-Authenticate": "Bearer"})
    if user.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="User account is inactive")
    return user


def require_roles(*roles: str):
    allowed = {normalize_role(role) for role in roles}

    async def dependency(current_user=Depends(get_current_user)):
        if normalize_role(current_user.role) not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action")
        return current_user
    return dependency
