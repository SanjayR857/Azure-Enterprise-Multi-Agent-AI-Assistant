from requests import status_codes
import os
import uuid
from pathlib import Path
import shutil
# pyre-ignore [missing-import]
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document

UPLOAD_DIR = Path.cwd() / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.xls', '.csv', '.txt', '.png', '.jpg', '.jpeg'}

class StorageService:
    def __init__(self):
        # Ensure the uploads directory exists when the service starts
        UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

    async def save_upload(self, db:AsyncSession, file:UploadFile, user_id:uuid.UUID, session_id: uuid.UUID):
        """
        Validates the file, securely saves it to disk, and tracks it in the database.
        """
        # validation the file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type:{ext}")
        # validation the file size
        await file.seek(0,2)
        file_size = file.tell()
        await file.seek(0)

        if file_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
            raise HTTPException(status_code=413, detail="File too large. Maximum size is {MAX_FILE_SIZE_MB} MB")
        
        # save the pysical file securely 
        secure_filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / secure_filename

        # we use a standard file write loop to save the chunks safely
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # create the database record
        new_doc = Document(
            user_id=user_id,
            session_id=session_id,
            original_filename=file.filename,
            storage_path=str(file_path),
            mime_type=file.content_type,
            file_size_bytes=file_size
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)

        return new_doc
    
storage_service = StorageService()

        
    
            
