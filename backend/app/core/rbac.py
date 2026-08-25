from fastapi import HTTPException, status

ROLE_TITLES = {
    "REQUESTER": "Employee / Requester",
    "SERVICE_DESK": "Service Desk Analyst L1",
    "RESOLVER": "Technical Support Engineer L2 / Application Support Engineer L3 / System Administrator",
    "INCIDENT_MANAGER": "Incident Manager",
    "CHANGE_MANAGER": "Change Manager",
    "IT_OPERATIONS": "IT Operations Engineer",
    "PLATFORM_ADMIN": "ITSM Platform Administrator",
    "KNOWLEDGE_MANAGER": "Knowledge Manager",
    "AUDITOR": "IT Auditor",
    "IT_MANAGER": "IT Operations Manager",
    "ADMIN": "Platform Administrator (legacy alias)",
    "USER": "Employee / Requester (legacy alias)",
}

MANAGE_USERS_ROLES = {"PLATFORM_ADMIN", "ADMIN"}
APPROVER_ROLES = {"PLATFORM_ADMIN", "ADMIN", "CHANGE_MANAGER", "INCIDENT_MANAGER", "IT_MANAGER"}
EXECUTOR_ROLES = {"PLATFORM_ADMIN", "ADMIN", "IT_OPERATIONS", "RESOLVER"}


def normalize_role(role: str | None) -> str:
    value = (role or "REQUESTER").strip().upper()
    return "REQUESTER" if value == "USER" else value


def ensure_role(role: str) -> str:
    normalized = normalize_role(role)
    if normalized not in ROLE_TITLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported WINGS role: {role}")
    return normalized


def require_user_management_role(user) -> None:
    if normalize_role(user.role) not in MANAGE_USERS_ROLES:
        raise HTTPException(status_code=403, detail="Only a Platform Administrator can manage users and roles.")


def can_manage_users(user) -> bool:
    return normalize_role(user.role) in MANAGE_USERS_ROLES


def can_approve(user) -> bool:
    return normalize_role(user.role) in APPROVER_ROLES


def can_execute(user) -> bool:
    return normalize_role(user.role) in EXECUTOR_ROLES
