import logging
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError
)

from app.core.config import settings
import aiofiles

logger = logging.getLogger(__name__)

class AzureBlobStorageService:


    def __init__(self, storage_account_name: str):
        try:
            self.account_url = (
                f"https://{storage_account_name}.blob.core.windows.net"
            )
            from typing import cast, Any
            self.credential = DefaultAzureCredential()
            self.service_client = BlobServiceClient(
                account_url=self.account_url,
                credential=cast(Any, self.credential)
            )
            logger.info("Connected to Azure Blob Storage", extra={"account_url": self.account_url})
        except AzureError as ex:
            logger.exception("Failed to connect to Azure Blob Storage", extra={"account_url": self.account_url, "error": str(ex)})
            raise ex

    async def close(self) -> None:
        """Closes the blob service client and credential, releasing network resources."""
        await self.service_client.close()
        await self.credential.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


    async def upload_file(self, container_name: str, blob_name: str, file_path: str) -> None:
        """
        Uploads a file to the specified container safely in chunks.
        """
        try: 
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            async def file_stream(f):
                while True:
                    chunk = await f.read(4096)
                    if not chunk:
                        break
                    yield chunk

            async with aiofiles.open(file=file_path, mode="rb") as f:
                await blob_client.upload_blob(data=file_stream(f), overwrite=True)
            logger.info("Successfully uploaded file", extra={"container_name": container_name, "blob_name": blob_name})
        except AzureError as ex:
            logger.exception("Failed to upload file", extra={"container_name": container_name, "blob_name": blob_name, "error": str(ex)})
            raise ex


    async def download_file(self, container_name: str, blob_name: str, file_path: str) -> None:
        """
        Downloads a file from the specified container.
        """
        try: 
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            stream = await blob_client.download_blob()
            async with aiofiles.open(file=file_path, mode="wb") as f:
                async for chunk in stream.chunks():
                    await f.write(chunk)
            logger.info("Successfully downloaded file", extra={"container_name": container_name, "blob_name": blob_name})
        except AzureError as ex:
            logger.exception("Failed to download file", extra={"container_name": container_name, "blob_name": blob_name, "error": str(ex)})
            raise ex


    async def delete_file(self, container_name: str, blob_name: str) -> None: 
        """
        Deletes a file from the specified container.
        """
        try:
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            await blob_client.delete_blob()
            logger.info("Successfully deleted file", extra={"container_name": container_name, "blob_name": blob_name})
        except AzureError as ex:
            logger.exception("Failed to delete file", extra={"container_name": container_name, "blob_name": blob_name, "error": str(ex)})
            raise ex
    
    async def list_files(self, container_name: str) -> list[str]:
        """
        Lists all files in the specified container.
        """
        try:
            blob_client = self.service_client.get_container_client(
                container=container_name
            )
            blobs = []
            async for blob in blob_client.list_blobs():
                blobs.append(blob.name)
            logger.info("Successfully listed files in container", extra={"container_name": container_name})
            return blobs
        except AzureError as ex:
            logger.exception("Failed to list files in container", extra={"container_name": container_name, "error": str(ex)})
            raise ex


    async def generate_download_sas(self, container_name: str, blob_name: str, expiry_hours: int = 1) -> str:
        """
        Generates a temporary Shared Access Signature (SAS) URL for downloading a blob.
        Uses User Delegation Key since we authenticate via DefaultAzureCredential.
        """
        from datetime import datetime, timedelta, timezone
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        try:
            now = datetime.now(timezone.utc)
            # Subtract 5 minutes to account for clock skew
            start_time = now - timedelta(minutes=5)
            expiry_time = now + timedelta(hours=expiry_hours)
            
            # Fetch the user delegation key from Azure
            user_delegation_key = await self.service_client.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time
            )
            
            # Generate the SAS token string
            sas_token = generate_blob_sas(
                account_name=self.service_client.account_name,
                container_name=container_name,
                blob_name=blob_name,
                account_key=None,
                user_delegation_key=user_delegation_key,
                permission=BlobSasPermissions(read=True),
                expiry=expiry_time,
                start=start_time
            )
            
            # Construct and return the full URL
            return f"{self.account_url}/{container_name}/{blob_name}?{sas_token}"
        except AzureError as ex:
            logger.exception("Failed to generate SAS token", extra={"container_name": container_name, "blob_name": blob_name, "error": str(ex)})
            raise ex


# Global blob storage service instance
_blob_service: AzureBlobStorageService | None = None

async def get_blob_service() -> AzureBlobStorageService:
    """Creates or returns a cached AzureBlobStorageService."""
    global _blob_service
    if _blob_service is None:
        _blob_service = AzureBlobStorageService(settings.STORAGE_ACCOUNT_NAME)
    return _blob_service

async def close_blob_service():
    """Closes the global AzureBlobStorageService gracefully."""
    global _blob_service
    if _blob_service is not None:
        await _blob_service.close()
        _blob_service = None
