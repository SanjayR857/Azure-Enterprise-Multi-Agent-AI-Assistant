# app/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from app.core.config import settings

# Use postgresql+asyncpg driver for async PostgreSQL
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Pool settings are critical for PostgreSQL in production!
engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=False,
    pool_size=20,          # Maximum number of permanent connections
    max_overflow=10,       # Allow up to 10 extra connections during spikes
    pool_timeout=30        # Seconds to wait for a connection before failing
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Database session dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields an async database session for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        yield session
