# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.conversation import router as conversation
from app.api.routes.attachments import router as attachments
api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(conversation)
api_router.include_router(attachments)

