# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.agents import router as agent_router
from app.api.routes.workflow import router as workflow_router
from app.api.routes.rag import router as rag_router

import sys
from contextlib import asynccontextmanager
from app.services.mcp_service import mcp_service

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


app.include_router(chat_router)
app.include_router(health_router)
app.include_router(agent_router)
app.include_router(workflow_router)
app.include_router(rag_router)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)

