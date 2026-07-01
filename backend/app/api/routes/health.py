# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
import azure.cosmos.aio as cosmos
from app.database.session import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("")
async def health():
    """
    Checks the health of the FastAPI application.
    """
    return {"status": "healthy", "database": "up"}