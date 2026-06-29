# app/database/session.py

# pyrefly: ignore [missing-import]
import azure.cosmos.aio as cosmos
# pyrefly: ignore [missing-import]
from azure.cosmos import PartitionKey
# pyrefly: ignore [missing-import]
import azure.cosmos.exceptions as exceptions
from typing import AsyncGenerator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def get_cosmos_client() -> cosmos.CosmosClient:
    """Creates an async CosmosClient."""
    return cosmos.CosmosClient(
        settings.AZURE_COSMOS_ENDPOINT, 
        credential=settings.AZURE_COSMOS_KEY
    )

async def init_db():
    """Initializes the database and container if they do not exist."""
    async with await get_cosmos_client() as client:
        try:
            # Create database
            database = await client.create_database_if_not_exists(id=settings.AZURE_COSMOS_DATABASE)
            
            # Create container partitioned by user_id
            # This is important for multi-tenant conversational apps
            #
            # Composite indexes optimize ORDER BY queries:
            #   - (session_id, sequence_number): for paginated message retrieval within a session
            #   - (type, created_at): for listing sessions sorted by recency
            indexing_policy = {
                "compositeIndexes": [
                    [
                        {"path": "/session_id", "order": "ascending"},
                        {"path": "/sequence_number", "order": "ascending"}
                    ],
                    [
                        {"path": "/type", "order": "ascending"},
                        {"path": "/created_at", "order": "descending"}
                    ]
                ]
            }
            
            await database.create_container_if_not_exists(
                id=settings.AZURE_COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/user_id"),
                offer_throughput=400,
                indexing_policy=indexing_policy
            )
            logger.info("Cosmos DB NoSQL Database and Container verified (with composite indexes).")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB initialization failed: {e}")
            raise

async def get_db() -> AsyncGenerator[cosmos.ContainerProxy, None]:
    """Yields an async Cosmos DB ContainerProxy for FastAPI routes."""
    # Note: the client must remain open during the request
    client = await get_cosmos_client()
    try:
        database = client.get_database_client(settings.AZURE_COSMOS_DATABASE)
        container = database.get_container_client(settings.AZURE_COSMOS_CONTAINER)
        yield container
    finally:
        await client.close()
