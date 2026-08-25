from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    return current_user
