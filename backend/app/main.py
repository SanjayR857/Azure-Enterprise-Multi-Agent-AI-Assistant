# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_router import api_router

import sys
from contextlib import asynccontextmanager
from app.services.mcp_service import mcp_service

"""
MCP servers run as separate processes.
We must use spawn to start them (child processes inherit handles differently).
`sys.executable` ensures we use the same Python interpreter.
`asynccontextmanager` ensures MCP connections persist for the app lifecycle.
"""
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Register MCP servers (process-based))
    mcp_service.register_server(
        "filesystem",
        [sys.executable, "app/mcp/servers/filesystem_mcp_server.py"]
    )

    await mcp_service.connect_all()
    yield

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

