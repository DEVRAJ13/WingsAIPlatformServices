from fastapi import APIRouter, Depends, status

from app.core.security import create_access_token
from app.api.dependencies import get_user_service
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    service: UserService = Depends(get_user_service),
):
    user = await service.authenticate_user(
        email=data.email,
        password=data.password,
    )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )