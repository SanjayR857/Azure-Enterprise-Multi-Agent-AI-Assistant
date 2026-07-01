from app.services.azure_agent_service import azure_agent_service
import logging
import uuid
import asyncio
from datetime import datetime
# pyrefly: ignore [missing-import]
import azure.cosmos.aio as cosmos
# pyrefly: ignore [missing-import]
import azure.cosmos.exceptions as exceptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AzureCosmosDBService:
    """
    Service class handling operations related to conversation history persistence and retrieval
    using Azure Cosmos DB NoSQL.
    """

    async def create_session(self, container: cosmos.ContainerProxy, user_id: uuid.UUID, session_id: uuid.UUID = None, title: str = None) -> dict:
        logger.info(f"Creating session for user {user_id} with title '{title}'")
        final_title = title
        if title:
            try:
                prompt = f"Generate a short, descriptive, and professional topic title (max 50 letters) for a conversation starting with this message: '{title}'. Respond ONLY with the title. No quotes, no punctuation, no conversational filler."
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None, azure_agent_service.run_chat, prompt)
                cleaned_title = response.strip('\"\'\n').strip()
                if cleaned_title:
                    final_title = cleaned_title
                else:
                    final_title = title[:50]
                logger.info(f"Generated title: {final_title}")
            except Exception as e:
                logger.error(f"Title generation failed: {e}")
                final_title = title[:50]
        
        doc_id = str(session_id or uuid.uuid4())
        user_id_str = str(user_id)
        
        session_doc = {
            "id": doc_id,
            "type": "session",
            "user_id": user_id_str,
            "title": final_title,
            "created_at": datetime.utcnow().isoformat(),
            # Omit "messages" array here for the new scalable pattern
        }
        
        try:
            await container.create_item(body=session_doc)
            logger.info(f"Successfully created session {doc_id}")
            return session_doc
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create chat session document: {e}")
            raise e

    async def get_session(self, container: cosmos.ContainerProxy, session_id: uuid.UUID, user_id: uuid.UUID) -> dict | None:
        logger.info(f"Retrieving session {session_id} for user {user_id}")
        try:
            # We partition by user_id
            response = await container.read_item(item=str(session_id), partition_key=str(user_id))
            logger.info(f"Successfully retrieved session {session_id}")
            return response
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Session {session_id} not found")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get chat session: {e}")
            raise e

    async def get_messages_for_session(
        self, 
        container: cosmos.ContainerProxy, 
        session_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> list[dict]:
        """
        Retrieve all standalone message documents for a specific session.
        Returns messages ordered by sequence_number ASC (oldest first).
        """
        logger.info(f"Retrieving messages for session {session_id}")
        try:
            # Query all messages for the session (very fast via index on session_id)
            query = "SELECT * FROM c WHERE c.type = 'message' AND c.session_id = @session_id"
            parameters = [{"name": "@session_id", "value": str(session_id)}]
            
            items = []
            async for item in container.query_items(query=query, parameters=parameters, partition_key=str(user_id)):
                items.append(item)
                
            # Sort in memory by sequence_number (fast for typical chat lengths)
            items.sort(key=lambda x: x.get("sequence_number", 0))
            
            logger.info(f"Retrieved {len(items)} messages for session {session_id}")
            return items
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to retrieve messages for session {session_id}: {e}")
            return []


    async def get_message_count_for_session(self, container: cosmos.ContainerProxy, session_id: uuid.UUID, user_id: uuid.UUID) -> int:
        """Get the total count of standalone messages for a session (used for pagination metadata)."""
        logger.info(f"Getting message count for session {session_id}")
        try:
            query = "SELECT VALUE COUNT(1) FROM c WHERE c.type = 'message' AND c.session_id = @session_id"
            parameters = [{"name": "@session_id", "value": str(session_id)}]
            async for item in container.query_items(query=query, parameters=parameters, partition_key=str(user_id)):
                logger.info(f"Counted {item} messages for session {session_id}")
                return item  # COUNT returns a single integer
            return 0
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to count messages for session {session_id}: {e}")
            return 0


    async def get_all_sessions(self, container: cosmos.ContainerProxy, user_id: uuid.UUID) -> list[dict]:
        """Retrieve all session documents (metadata only, no messages) for the user."""
        logger.info(f"Retrieving all sessions for user {user_id}")
        try:
            query = "SELECT c.id, c.title, c.is_pinned, c.created_at FROM c WHERE c.type = 'session' AND c.user_id = @user_id ORDER BY c.created_at DESC"
            parameters = [{"name": "@user_id", "value": str(user_id)}]
            
            items = []
            async for item in container.query_items(query=query, parameters=parameters, partition_key=str(user_id)):
                items.append(item)
            logger.info(f"Retrieved {len(items)} sessions for user {user_id}")
            return items
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to retrieve all sessions: {e}")
            return []

    async def add_message(
        self, 
        container: cosmos.ContainerProxy, 
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str, 
        content: str, 
        sequence_number: int,
        attachments: list[dict] | None = None
    ) -> dict:
        logger.info(f"Adding {role} message to session {session_id} (seq: {sequence_number})")
        message_doc = {
            "id": str(uuid.uuid4()),
            "type": "message",
            "session_id": str(session_id),
            "user_id": str(user_id),
            "role": role,
            "content": content,
            "sequence_number": sequence_number,
            "attachments": attachments,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            await container.create_item(body=message_doc)
            logger.info(f"Successfully added message {message_doc['id']}")
            return message_doc
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to add message to document: {e}")
            raise e

    async def delete_session(self, container: cosmos.ContainerProxy, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        logger.info(f"Deleting session {session_id} for user {user_id}")
        try:
            # Delete session doc
            await container.delete_item(item=str(session_id), partition_key=str(user_id))
            
            # Cascade delete standalone messages
            messages = await self.get_messages_for_session(container, session_id, user_id)
            for msg in messages:
                try:
                    await container.delete_item(item=msg["id"], partition_key=str(user_id))
                except Exception as e:
                    logger.error(f"Failed to delete standalone message {msg['id']} during cascade delete: {e}")
            
            logger.info(f"Successfully deleted session {session_id} and its messages")
            return True
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Session {session_id} not found for deletion")
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise e


    async def update_message(
        self, 
        container: cosmos.ContainerProxy, 
        message_id: uuid.UUID, 
        content: str,
        user_id: uuid.UUID
    ) -> dict | None:
        logger.info(f"Updating message {message_id} for user {user_id}")
        # Try updating standalone message first
        try:
            msg_doc = await container.read_item(item=str(message_id), partition_key=str(user_id))
            if msg_doc.get("type") == "message":
                msg_doc["content"] = content
                await container.replace_item(item=msg_doc["id"], body=msg_doc)
                logger.info(f"Successfully updated standalone message {message_id}")
                return msg_doc
        except exceptions.CosmosResourceNotFoundError:
            pass # Fall through to legacy embedded logic
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update standalone message {message_id}: {e}")

        # Legacy embedded logic
        logger.info(f"Falling back to legacy embedded logic for updating message {message_id}")
        try:
            query = "SELECT * FROM c WHERE c.type = 'session' AND c.user_id = @user_id"
            parameters = [{"name": "@user_id", "value": str(user_id)}]
            
            async for doc in container.query_items(query=query, parameters=parameters, partition_key=str(user_id)):
                updated = False
                for m in doc.get("messages", []):
                    if m.get("id") == str(message_id):
                        m["content"] = content
                        updated = True
                        break
                
                if updated:
                    await container.replace_item(item=doc["id"], body=doc)
                    # Inject parent session id into the returned message dict
                    m["session_id"] = doc["id"]
                    logger.info(f"Successfully updated embedded message {message_id} in session {doc['id']}")
                    return m
            logger.warning(f"Message {message_id} not found in embedded messages")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update message {message_id}: {e}")
            raise e

azure_cosmos_db_service = AzureCosmosDBService()
