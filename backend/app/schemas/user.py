from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "REQUESTER"
    employee_id: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=150)
    designation: str | None = Field(default=None, max_length=150)
    manager_name: str | None = Field(default=None, max_length=150)
    status: str = "ACTIVE"
    must_change_password: bool = True


class AdminUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    temporary_password: str = Field(min_length=8, max_length=128)
    role: str = "REQUESTER"
    employee_id: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=150)
    designation: str | None = Field(default=None, max_length=150)
    manager_name: str | None = Field(default=None, max_length=150)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    employee_id: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=150)
    designation: str | None = Field(default=None, max_length=150)
    manager_name: str | None = Field(default=None, max_length=150)
    status: str | None = None
    role: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class AdminPasswordResetRequest(BaseModel):
    temporary_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    employee_id: str | None = None
    department: str | None = None
    designation: str | None = None
    manager_name: str | None = None
    status: str
    must_change_password: bool
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
