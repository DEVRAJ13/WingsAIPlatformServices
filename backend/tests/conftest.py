import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-production")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DEBUG", "false")
