from contextlib import asynccontextmanager

from fastapi import FastAPI

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
from app.api.v1.users import router as users_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="WINGS AI Platform",
    description="AI-native enterprise IT operations platform",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"],
)

app.include_router(
    ai_router,
    prefix="/api/v1/ai",
    tags=["AI"],
)

app.include_router(
    rag_router,
    prefix="/api/v1/ai",
    tags=["AI / RAG"],
)

app.include_router(
    agent_router,
    prefix="/api/v1/ai/agent",
    tags=["AI Agents"],
)

app.include_router(
    incidents_router,
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)

app.include_router(
    approvals_router,
    prefix="/api/v1",
    tags=["Approvals"],
)

app.include_router(
    approval_execution_router,
    prefix="/api/v1",
    tags=["Approval Execution"],
)

app.include_router(
    documents_router,
    prefix="/api/v1",
    tags=["Documents"],
)

app.include_router(
    health_router,
)