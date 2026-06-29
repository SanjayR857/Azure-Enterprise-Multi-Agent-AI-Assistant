# pyrefly: ignore [missing-import]
from azure.identity import DefaultAzureCredential
# pyrefly: ignore [missing-import]
from azure.storage.blob import BlobServiceClient

account_url = "https://<storageaccountname>.blob.core.windows.net"
default_credential = DefaultAzureCredential()

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url, credential=default_credential)
