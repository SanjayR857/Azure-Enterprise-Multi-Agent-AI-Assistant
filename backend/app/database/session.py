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

# Global client instance
_cosmos_client: cosmos.CosmosClient | None = None

async def get_cosmos_client() -> cosmos.CosmosClient:
    """Creates or returns a cached async CosmosClient."""
    global _cosmos_client
    if _cosmos_client is None:
        _cosmos_client = cosmos.CosmosClient(
            settings.AZURE_COSMOS_ENDPOINT, 
            credential=settings.AZURE_COSMOS_KEY
        )
    return _cosmos_client

async def close_cosmos_client():
    """Closes the global CosmosClient gracefully."""
    global _cosmos_client
    if _cosmos_client is not None:
        await _cosmos_client.close()
        _cosmos_client = None

async def init_db():
    """Initializes the database and container if they do not exist."""
    client = await get_cosmos_client()
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
        # type: ignore
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
    # We do NOT close the client here because it's a shared global singleton
    client = await get_cosmos_client()
    database = client.get_database_client(settings.AZURE_COSMOS_DATABASE)
    container = database.get_container_client(settings.AZURE_COSMOS_CONTAINER)
    yield container