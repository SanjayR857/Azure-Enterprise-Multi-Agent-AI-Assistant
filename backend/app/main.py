# pyrefly: ignore [missing-import]
from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.agents import router as agent_router

app = FastAPI(
    title="Enterprise Multi-Agent AI Assistant",
    version="0.0.1",
)

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(agent_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
