import os
import uuid
from pathlib import Path
import shutil
import logging
from datetime import datetime
# pyre-ignore [missing-import]
from fastapi import UploadFile, HTTPException
# pyrefly: ignore [missing-import]
import azure.cosmos.aio as cosmos
# pyrefly: ignore [missing-import]
import azure.cosmos.exceptions as exceptions

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path.cwd() / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.xls', '.csv', '.txt', '.png', '.jpg', '.jpeg'}

class StorageService:
    def __init__(self):
        # Ensure the uploads directory exists when the service starts
        UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

    async def save_upload(self, container: cosmos.ContainerProxy, file: UploadFile, user_id: uuid.UUID, session_id: uuid.UUID) -> dict:
        """
        Validates the file, securely saves it to disk, and tracks it in the Cosmos DB.
        """
        logger.info(f"Starting file upload for {file.filename} by user {user_id}")
        # validation the file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            logger.error(f"Upload failed: Unsupported file type {ext}")
            raise HTTPException(status_code=400, detail=f"Unsupported file type:{ext}")
        # validation the file size
        await file.seek(0,2)
        file_size = file.tell()
        await file.seek(0)

        if file_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
            logger.error(f"Upload failed: File size {file_size} exceeds {MAX_FILE_SIZE_MB}MB limit")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB")
        
        # save the physical file securely 
        secure_filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / secure_filename

        logger.info(f"Saving physical file to {file_path}")
        # we use a standard file write loop to save the chunks safely
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # create the database record for Cosmos DB
        doc_id = str(uuid.uuid4())
        user_id_str = str(user_id)
        
        document_doc = {
            "id": doc_id,
            "type": "document",
            "user_id": user_id_str,
            "session_id": str(session_id),
            "original_filename": file.filename,
            "storage_path": str(file_path),
            "mime_type": file.content_type,
            "file_size_bytes": file_size,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            await container.create_item(body=document_doc)
            logger.info(f"Successfully saved document metadata for {doc_id} to Cosmos DB")
            return document_doc
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to save document metadata: {e}")
            raise HTTPException(status_code=500, detail="Failed to save document metadata to Cosmos DB")

storage_service = StorageService()
