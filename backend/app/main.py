from fastapi import FastAPI
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Wings AI Platform",
    description="A platform for AI-powered applications and services.",
    version="1.0.0",
    )

app.include_router(health_router)