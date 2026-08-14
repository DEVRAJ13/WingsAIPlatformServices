from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
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


app.include_router(health_router)
app.include_router(users_router)