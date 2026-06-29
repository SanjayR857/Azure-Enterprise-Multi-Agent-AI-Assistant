# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
import azure.cosmos.aio as cosmos
from app.database.session import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("")
async def health(container: cosmos.ContainerProxy = Depends(get_db)):
    """
    Checks the health of the application and the Cosmos DB connection.
    """
    try:
        # Read the container properties to verify connectivity
        await container.read()
        return {"status": "healthy", "database": "up"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")