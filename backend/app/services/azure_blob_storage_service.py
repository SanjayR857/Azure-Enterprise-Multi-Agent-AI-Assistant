from langsmith import expect
import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError
)

from app.core.config import settings
import aiofiles

logger = logging.getLogger(__name__)


class AzureBlobStorageService:
    async def __init__(self, storage_account_name: str):
        try:
            self.account_url = (
                f"https://{storage_account_name}.blob.core.windows.net"
            )
            self.credential = DefaultAzureCredential()
            self.service_client = BlobServiceClient(
                account_url=self.account_url,
                credential=self.credential
            )
            logger.info(f"Connected to Azure Blob Storage")
        except AzureError as ex:
            logger.exception(f"Failed to connect to Azure Blob Storage: {ex}")
            raise ex

    async def upload_file(self, container_name: str, blob_name: str, file_path:str):
        """
        Uploads a file to the specified container.
        """
        try: 
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob = blob_name
            )
            async with aiofiles.open(file=file_path, mode="rb") as data:
                await blob_client.upload_blob(data, overwrite=True)
            logger.info(f"Successfully uploaded file: {blob_name}")
        except AzureError as ex:
            logger.exception(f"Failed to upload file: {blob_name}")
            raise ex

    def get_container_client(self, container_name: str):
        return self.service_client.get_container_client(container_name)