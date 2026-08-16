from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:

        existing_user = await self.repository.get_by_email(
            data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
        )

        return await self.repository.create(user)

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User:

        user = await self.repository.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    async def get_user(self, user_id: int) -> User:

        user = await self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:

        return await self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    async def update_user(
        self,
        user_id: int,
        data: UserUpdate,
    ) -> User:

        user = await self.get_user(user_id)

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "email" in update_data:
            existing_user = await self.repository.get_by_email(
                update_data["email"]
            )

            if (
                existing_user
                and existing_user.id != user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already belongs to another user",
                )

        for field, value in update_data.items():
            setattr(user, field, value)

        return await self.repository.create(user)

    async def delete_user(self, user_id: int) -> None:

        user = await self.get_user(user_id)

        await self.repository.delete(user)