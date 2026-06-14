# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database.session import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Checks the health of the application and the database.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "up"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")