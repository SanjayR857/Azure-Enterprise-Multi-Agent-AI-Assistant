# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_router import api_router
from app.core.logging import setup_logging
from app.core.security import azure_scheme
# Initialize logging configuration
setup_logging()

import logging
import sys
from contextlib import asynccontextmanager
from app.database.session import init_db
from app.services.mcp_service import mcp_service

logger = logging.getLogger(__name__)

"""
lifecycle management for MCP servers and database pools
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    

    # Load OpenID config on startup
    logger.info("Loading OpenID config on startup...")
    await azure_scheme.openid_config.load_config()
    logger.info("OpenID config loaded successfully.")

    # Initialize Cosmos DB NoSQL database and container
    logger.info("Initializing Cosmos DB NoSQL tables...")
    await init_db()
    logger.info("Cosmos DB NoSQL tables verified/created successfully.")

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
    logger.info("Shutdown complete.")

app = FastAPI(
    title="Enterprise Multi-Agent AI Assistant",
    version="0.0.1",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
        'scopes': settings.SCOPE_NAME,
    },
)


# Enable CORS for frontend UI connection
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
