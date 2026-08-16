from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.v1.auth import router as auth_router
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

app.include_router(health_router)
app.include_router(users_router)