# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_router import api_router
from app.core.logging import setup_logging

# Initialize logging configuration
setup_logging()

import logging
import sys
from contextlib import asynccontextmanager
from app.services.mcp_service import mcp_service

logger = logging.getLogger(__name__)

"""
lifecycle management for MCP servers and database pools
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    
    # Initialize database tables
    logger.info("Initializing database tables...")
    from app.database.session import engine
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created successfully.")

    # Register and connect MCP servers
    logger.info("Registering MCP servers...")
    mcp_service.register_server(
        "filesystem",
        [sys.executable, "app/mcp/servers/filesystem_mcp_server.py"]
    )

    logger.info("Connecting to registered MCP servers...")
    await mcp_service.connect_all()
    logger.info("MCP servers connected successfully.")
    
    logger.info("Application startup complete. Ready to receive requests.")
    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")
    logger.info("Disposing database connection pool...")
    await engine.dispose()
    logger.info("Database connection pool disposed. Shutdown complete.")

app = FastAPI(
    title="Enterprise Multi-Agent AI Assistant",
    version="0.0.1",
    lifespan=lifespan
)
# Enable CORS for frontend UI connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)

