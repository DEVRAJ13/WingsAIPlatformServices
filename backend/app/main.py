from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.v1.ai import router as ai_router
from app.api.v1.agent import router as agent_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.approval_execution import (
    router as approval_execution_router,
)
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.rag import router as rag_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.users import router as users_router
from app.api.routes.users import router as users_crud_router
from app.db.init_db import init_db
from app.core.config import settings
from app.db.database import engine


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="WINGS AI Platform",
    description="AI-native enterprise IT operations platform",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# CORS
# =========================================================
#
# React/Vite frontend:
#   http://localhost:5173
#
# Also allow:
#   http://127.0.0.1:5173
#
# This is required for browser requests such as:
#   POST /api/v1/auth/login
#
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# AUTHENTICATION
# =========================================================

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# =========================================================
# USERS
# =========================================================

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"],
)

app.include_router(
    users_crud_router,
    prefix="/api/v1",
    tags=["User Administration"],
)


# =========================================================
# AI
# =========================================================

app.include_router(
    ai_router,
    prefix="/api/v1/ai",
    tags=["AI"],
)


# =========================================================
# RAG
# =========================================================

app.include_router(
    rag_router,
    prefix="/api/v1/ai",
    tags=["AI / RAG"],
)


# =========================================================
# AI AGENTS
# =========================================================

app.include_router(
    agent_router,
    prefix="/api/v1/ai/agent",
    tags=["AI Agents"],
)


# =========================================================
# INCIDENTS
# =========================================================

app.include_router(
    incidents_router,
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)


# =========================================================
# APPROVALS
# =========================================================

app.include_router(
    approvals_router,
    prefix="/api/v1",
    tags=["Approvals"],
)


# =========================================================
# APPROVAL EXECUTION
# =========================================================

app.include_router(
    approval_execution_router,
    prefix="/api/v1",
    tags=["Approval Execution"],
)


# =========================================================
# DOCUMENTS / KNOWLEDGE
# =========================================================

app.include_router(
    documents_router,
    prefix="/api/v1",
    tags=["Documents"],
)


# =========================================================
# HEALTH
# =========================================================

app.include_router(
    monitoring_router,
    prefix="/api/v1/monitoring",
    tags=["Monitoring"],
)

app.include_router(
    health_router,
)