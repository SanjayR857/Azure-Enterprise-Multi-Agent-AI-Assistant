# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat
from app.api.routes.rag import router as rag_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(chat)
api_router.include_router(rag_router)
