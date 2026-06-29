import uuid
import asyncio
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import azure.cosmos.aio as cosmos

from app.database.session import get_db
from app.api.dependencies.auth import validate_user
from app.schemas.user_schema import User
from app.services.storage_service import storage_service
from app.services.document_parser import document_parser

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(validate_user)]
)

@router.post("/upload")
async def upload_document(
    session_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    container: cosmos.ContainerProxy = Depends(get_db),
    current_user: User = Depends(validate_user)
):
    logger.info(f"Received document upload request: {file.filename} for session {session_id}")
    try:
        # 1. Save the physical file & track it in the DB using the Storage Service
        db_doc = await storage_service.save_upload(container, file, current_user.id, session_id)
        
        # 2. Trigger the RAG parser in the background!
        # By using asyncio.create_task, the API instantly returns "Success" to the user
        # while the server secretly crunches the 100-page PDF in the background.
        logger.info(f"Triggering background parsing task for {db_doc['id']}")
        asyncio.create_task(document_parser.process_and_index(db_doc))

        logger.info(f"Upload successful for {file.filename}")
        return {
            "status": "success",
            "document_id": str(db_doc["id"]),
            "filename": db_doc["original_filename"],
            "message": "File uploaded and is being processed into the Vector DB."
        }
    except HTTPException as he:
        logger.warning(f"HTTPException during document upload: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during document upload: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
