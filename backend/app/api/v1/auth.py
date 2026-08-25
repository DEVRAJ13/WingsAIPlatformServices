from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user, get_user_service
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import PasswordChangeRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_403_FORBIDDEN)
async def register():
    raise HTTPException(status_code=403, detail="Self-registration is disabled. Contact the WINGS Platform Administrator for an account.")


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, service: UserService = Depends(get_user_service)):
    user = await service.authenticate_user(data.email, data.password)
    access_token = create_access_token(user_id=user.id, role=user.role, must_change_password=user.must_change_password, token_version=user.token_version)
    return TokenResponse(access_token=access_token, user=user, must_change_password=user.must_change_password)


@router.post("/change-password", response_model=UserResponse)
async def change_password(
    data: PasswordChangeRequest,
    current_user=Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.change_password(current_user, data)
