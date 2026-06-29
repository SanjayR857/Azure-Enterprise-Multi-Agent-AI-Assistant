# pyrefly: ignore [missing-import]
from fastapi import Security, Depends
import azure.cosmos.aio as cosmos
import azure.cosmos.exceptions as exceptions
from datetime import datetime
import uuid

from app.database.session import get_db
from app.schemas.user_schema import User
from app.core.security import azure_scheme
import logging

logger = logging.getLogger(__name__)

async def validate_user(
    token_user: dict = Security(azure_scheme),
    container: cosmos.ContainerProxy = Depends(get_db)
):
    """
    Validates the Azure AD token and syncs the user to the local Cosmos DB.
    Production Standard: You can add RBAC (Role-Based Access Control) 
    or database lookups here later if needed.
    """
    oid = token_user.claims.get("oid") if hasattr(token_user, "claims") else token_user.get("oid")
    email = (token_user.claims.get("preferred_username") or token_user.claims.get("email")) if hasattr(token_user, "claims") else (token_user.get("preferred_username") or token_user.get("email"))
    name = token_user.claims.get("name") if hasattr(token_user, "claims") else token_user.get("name")

    if not oid:
        # Fallback if somehow oid is missing
        return None

    # Check if user exists in local DB
    user = None
    try:
        query = "SELECT * FROM c WHERE c.type = 'user' AND c.azure_oid = @oid"
        parameters = [{"name": "@oid", "value": oid}]
        
        # Depending on partition strategy, user partition key might be their ID
        # Since we query by azure_oid, we might do cross-partition or have a users container.
        # Assuming the single container holds users too, partitioned by their id.
        async for item in container.query_items(query=query, parameters=parameters):
            user = User(**item)
            break
            
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"Failed to query user: {e}")
        pass

    if not user:
        # Auto-provision user on first login
        doc_id = str(uuid.uuid4())
        user_doc = {
            "id": doc_id,
            "user_id": doc_id, # partition key
            "type": "user",
            "azure_oid": oid,
            "email": email or "",
            "name": name or "",
            "created_at": datetime.utcnow().isoformat()
        }
        try:
            await container.create_item(body=user_doc)
            user = User(**user_doc)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create user document: {e}")
            raise

    return user
