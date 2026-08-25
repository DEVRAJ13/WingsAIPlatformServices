from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def save(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(func.lower(User.email) == email.lower()))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.id.desc()).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def count_active_admins(self) -> int:
        result = await self.db.execute(
            select(func.count(User.id)).where(
                User.status == "ACTIVE",
                User.role.in_(["PLATFORM_ADMIN", "ADMIN"]),
            )
        )
        return int(result.scalar_one())

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
