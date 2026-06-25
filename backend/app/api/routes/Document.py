import uuid
import asyncio
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.dependencies.auth import validate_user
from app.models.user import User
from app.services.storage_service import storage_service
from app.services.document_parser import document_parser

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(validate_user)]
)

@router.post("/upload")
async def upload_document(
    session_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(validate_user)
):
    try:
        # 1. Save the physical file & track it in the DB using the Storage Service
        db_doc = await storage_service.save_upload(db, file, current_user.id, session_id)
        
        # 2. Trigger the RAG parser in the background!
        # By using asyncio.create_task, the API instantly returns "Success" to the user
        # while the server secretly crunches the 100-page PDF in the background.
        asyncio.create_task(document_parser.process_and_index(db_doc))

        return {
            "status": "success",
            "document_id": str(db_doc.id),
            "filename": db_doc.original_filename,
            "message": "File uploaded and is being processed into the Vector DB."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
