from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_user_service, require_roles
from app.core.rbac import ROLE_TITLES
from app.schemas.user import AdminPasswordResetRequest, AdminUserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/roles")
async def get_roles(current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN"))):
    return {"roles": [{"key": key, "title": title} for key, title in ROLE_TITLES.items() if key not in {"USER", "ADMIN"}]}


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: AdminUserCreate,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN")),
    service: UserService = Depends(get_user_service),
):
    return await service.create_admin_user(data)


@router.get("", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN")),
    service: UserService = Depends(get_user_service),
):
    return await service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN")), service: UserService = Depends(get_user_service)):
    return await service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN")),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user_id, data, actor=current_user)


@router.post("/{user_id}/reset-password", response_model=UserResponse)
async def reset_password(
    user_id: int,
    payload: AdminPasswordResetRequest,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN")),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Use Settings → Change Password to change your own password.")
    return await service.reset_password(user_id, payload.temporary_password)


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_status(
    user_id: int,
    payload: dict,
    current_user=Depends(require_roles("PLATFORM_ADMIN", "ADMIN")),
    service: UserService = Depends(get_user_service),
):
    status_value = str(payload.get("status") or "").upper()
    if status_value not in {"ACTIVE", "INACTIVE"}:
        raise HTTPException(status_code=400, detail="Status must be ACTIVE or INACTIVE")
    return await service.update_user(user_id, UserUpdate(status=status_value), actor=current_user)
