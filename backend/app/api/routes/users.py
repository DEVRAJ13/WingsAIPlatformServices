from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_user_service
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(data)


@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: UserService = Depends(get_user_service),
):
    return await service.get_users(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(
        user_id,
        data,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)