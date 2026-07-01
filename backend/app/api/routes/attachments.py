import uuid
import logging
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import azure.cosmos.aio as cosmos

from app.database.session import get_db
from app.api.dependencies.auth import validate_user
from app.schemas.user_schema import User
from app.schemas.attachment_schema import AttachmentResponse    
from app.services.azure_blob_storage_service import AzureBlobStorageService, get_blob_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
    dependencies=[Depends(validate_user)]
)

# Notice the response_model here!
@router.post("/upload", response_model=AttachmentResponse)
async def upload_attachment(
    session_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    container: cosmos.ContainerProxy = Depends(get_db),
    current_user: User = Depends(validate_user),
    blob_service: AzureBlobStorageService = Depends(get_blob_service)
):
    logger.info(f"Received attachment upload: {file.filename} for session {session_id}")
    
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.ALLOWED_ATTACHMENT_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported attachment extension: {ext}")
        
    if file.content_type not in settings.ALLOWED_ATTACHMENT_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported attachment MIME type: {file.content_type}")
        
    # file.size is available in FastAPI 0.100+
    file_size = file.size if getattr(file, 'size', None) is not None else 0
    if file_size and file_size > (settings.MAX_ATTACHMENT_SIZE_MB * 1024 * 1024):
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {settings.MAX_ATTACHMENT_SIZE_MB} MB")

    # Create a virtual folder structure in Blob Storage!
    secure_filename = f"{current_user.id}/{session_id}/{uuid.uuid4()}{ext}"
    container_name = "chat-attachments"
    
    try:
        # Use our updated production-ready Blob Storage service
        blob_client = blob_service.service_client.get_blob_client(
            container=container_name,
            blob=secure_filename
        )
        # Upload physical file
        await blob_client.upload_blob(data=file.file, overwrite=True)
            
        # Create metadata tracking document for Cosmos DB
        attachment_doc = {
            "id": str(uuid.uuid4()),
            "type": "attachment",
            "user_id": str(current_user.id),
            "session_id": str(session_id),
            "original_filename": file.filename or "unknown",
            "blob_name": secure_filename,
            "mime_type": file.content_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to Cosmos DB
        await container.create_item(body=attachment_doc)
        logger.info(f"Successfully saved attachment metadata to Cosmos DB")
        
        # Return the data that perfectly matches our AttachmentResponse Pydantic schema!
        return AttachmentResponse(
            id=uuid.UUID(attachment_doc["id"]),
            original_filename=attachment_doc["original_filename"],
            mime_type=attachment_doc["mime_type"],
            session_id=uuid.UUID(attachment_doc["session_id"]),
            created_at=datetime.fromisoformat(attachment_doc["created_at"])
        )
        
    except Exception as e:
        logger.error(f"Error during attachment upload: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    container: cosmos.ContainerProxy = Depends(get_db),
    current_user: User = Depends(validate_user),
    blob_service: AzureBlobStorageService = Depends(get_blob_service)
):
    try:
        # Fetch metadata using a query to avoid partition key guesswork
        from typing import Any
        query = "SELECT * FROM c WHERE c.id = @id AND c.type = 'attachment'"
        parameters: list[dict[str, Any]] = [{"name": "@id", "value": attachment_id}]
        items = [item async for item in container.query_items(query=query, parameters=parameters)]
        
        if not items:
            raise HTTPException(status_code=404, detail="Attachment not found")
            
        attachment_meta = items[0]
        
        # Security: Verify the attachment belongs to the requesting user
        if attachment_meta.get("user_id") != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden")
            
        blob_name = attachment_meta.get("blob_name")
        if not blob_name:
            raise HTTPException(status_code=404, detail="Blob not found")
            
        # Generate the SAS token URL
        sas_url = await blob_service.generate_download_sas(
            container_name="chat-attachments",
            blob_name=blob_name,
            expiry_hours=1
        )
        return {"download_url": sas_url}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to generate download URL for {attachment_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: str,
    container: cosmos.ContainerProxy = Depends(get_db),
    current_user: User = Depends(validate_user),
    blob_service: AzureBlobStorageService = Depends(get_blob_service)
):
    logger.info(f"Received request to delete attachment: {attachment_id}")
    try:
        from typing import Any
        query = "SELECT * FROM c WHERE c.id = @id AND c.type = 'attachment'"
        parameters: list[dict[str, Any]] = [{"name": "@id", "value": attachment_id}]
        items = [item async for item in container.query_items(query=query, parameters=parameters)]
        
        if not items:
            # Maybe already deleted, return success
            return {"status": "success", "message": "Attachment not found or already deleted"}
            
        attachment_meta = items[0]
        
        if attachment_meta.get("user_id") != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden")
            
        blob_name = attachment_meta.get("blob_name")
        
        # 1. Delete from Blob Storage
        if blob_name:
            try:
                await blob_service.delete_file("chat-attachments", blob_name)
            except Exception as e:
                logger.error(f"Failed to delete blob {blob_name}: {e}")
                # We can still proceed to delete the DB record if the blob is missing
                
        # 2. Delete from Cosmos DB
        # Note: We don't have a specific partition key mapping here if it's not user_id.
        # Wait, the partition key is user_id for everything?
        # Let's check `attachment_doc`: "user_id": str(current_user.id)
        # Yes, partition key is user_id
        await container.delete_item(item=attachment_id, partition_key=str(current_user.id))
        
        return {"status": "success", "message": "Attachment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete attachment {attachment_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
