from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select

from app.core.rbac import ensure_role, normalize_role
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserCreate, PasswordChangeRequest, UserCreate, UserUpdate

VALID_ROLES = {
    "REQUESTER", "SERVICE_DESK", "RESOLVER", "INCIDENT_MANAGER", "CHANGE_MANAGER",
    "IT_OPERATIONS", "PLATFORM_ADMIN", "KNOWLEDGE_MANAGER", "AUDITOR", "IT_MANAGER", "ADMIN",
}


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(str(data.email).lower())
        if existing_user:
            raise HTTPException(status_code=409, detail="User with this email already exists")
        role = ensure_role(data.role)
        status_value = data.status.upper()
        if status_value not in {"ACTIVE", "INACTIVE"}:
            raise HTTPException(status_code=400, detail="User status must be ACTIVE or INACTIVE")
        user = User(
            name=data.name.strip(), email=str(data.email).lower(), password_hash=hash_password(data.password),
            role=role, employee_id=data.employee_id, department=data.department,
            designation=data.designation, manager_name=data.manager_name, status=status_value,
            must_change_password=data.must_change_password,
        )
        return await self.repository.create(user)

    async def create_admin_user(self, data: AdminUserCreate) -> User:
        return await self.create_user(UserCreate(
            name=data.name, email=data.email, password=data.temporary_password, role=data.role,
            employee_id=data.employee_id, department=data.department, designation=data.designation,
            manager_name=data.manager_name, status="ACTIVE", must_change_password=True,
        ))

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.repository.get_by_email(email.lower())
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
        if normalize_role(user.role) not in VALID_ROLES:
            raise HTTPException(status_code=403, detail="User has no valid WINGS role")
        if user.status != "ACTIVE":
            raise HTTPException(status_code=403, detail="User account is inactive. Contact the Platform Administrator.")
        user.last_login_at = datetime.now(timezone.utc)
        return await self.repository.save(user)

    async def change_password(self, user: User, data: PasswordChangeRequest) -> User:
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        if data.current_password == data.new_password:
            raise HTTPException(status_code=400, detail="New password must be different from the current password")
        user.password_hash = hash_password(data.new_password)
        user.must_change_password = False
        user.token_version += 1
        return await self.repository.save(user)

    async def reset_password(self, user_id: int, temporary_password: str) -> User:
        user = await self.get_user(user_id)
        user.password_hash = hash_password(temporary_password)
        user.must_change_password = True
        user.token_version += 1
        return await self.repository.save(user)

    async def get_user(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update_user(self, user_id: int, data: UserUpdate, actor: User | None = None) -> User:
        user = await self.get_user(user_id)
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"]:
            update_data["email"] = str(update_data["email"]).lower()
            existing = await self.repository.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Email already belongs to another user")
        if "role" in update_data and update_data["role"] is not None:
            update_data["role"] = ensure_role(update_data["role"])
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].upper()
            if update_data["status"] not in {"ACTIVE", "INACTIVE"}:
                raise HTTPException(status_code=400, detail="User status must be ACTIVE or INACTIVE")

        if actor and actor.id == user.id:
            if update_data.get("status") == "INACTIVE":
                raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
            if "role" in update_data and normalize_role(update_data["role"]) not in {"PLATFORM_ADMIN", "ADMIN"}:
                raise HTTPException(status_code=400, detail="You cannot remove your own Platform Administrator role.")

        if "role" in update_data and normalize_role(user.role) in {"PLATFORM_ADMIN", "ADMIN"} and normalize_role(update_data["role"]) not in {"PLATFORM_ADMIN", "ADMIN"}:
            admins = await self.repository.count_active_admins()
            if admins <= 1:
                raise HTTPException(status_code=400, detail="At least one active Platform Administrator must remain.")

        if update_data.get("status") == "INACTIVE" and normalize_role(user.role) in {"PLATFORM_ADMIN", "ADMIN"}:
            admins = await self.repository.count_active_admins()
            if admins <= 1:
                raise HTTPException(status_code=400, detail="At least one active Platform Administrator must remain.")

        for field, value in update_data.items():
            setattr(user, field, value)
        return await self.repository.save(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user(user_id)
        await self.repository.delete(user)
