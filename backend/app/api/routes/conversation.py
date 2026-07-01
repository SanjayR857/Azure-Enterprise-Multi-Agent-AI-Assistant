# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.azure_agent_service import azure_agent_service
from app.utils import count_tokens
from app.database.session import get_db
from app.services.azure_cosmos_db_service import azure_cosmos_db_service
# pyrefly: ignore [missing-import]
import azure.cosmos.aio as cosmos
# pyrefly: ignore [missing-import]
from app.api.dependencies.auth import validate_user
from app.schemas.user_schema import User
from app.schemas.conversation_schema import (
    AgentRequest,
    ConversationMessageUpdate,
    ConversationMessageResponse,
    SessionHistoryResponse,
    AllSessionsResponse,
    MessageDetails
)
import uuid
import asyncio
import logging
import json
# pyrefly: ignore [missing-import]
from fastapi.responses import StreamingResponse
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(validate_user)]
)

@router.post("")
async def conversation(request: AgentRequest, container: cosmos.ContainerProxy = Depends(get_db), current_user: User = Depends(validate_user)):
    """
    Handles incoming user messages, triggers the agent orchestrator, 
    persists the exchange to the conversation history, and returns the response.
    """
    logger.info(f"Received new chat message from user {current_user.id} for session {request.session_id}")
    session_id = request.session_id or uuid.uuid4()
    logger.info(f"Incoming request.session_id: {request.session_id}, final session_id: {session_id}")
    
    try:
        session = await azure_cosmos_db_service.get_session(container, session_id, current_user.id)
        if not session:
            session = await azure_cosmos_db_service.create_session(container, user_id=current_user.id, session_id=session_id, title=request.message)
            seq = 0
        else:
            standalone_count = await azure_cosmos_db_service.get_message_count_for_session(container, session_id, current_user.id)
            seq = len(session.get("messages", [])) + standalone_count
        
        # Save user message
        await azure_cosmos_db_service.add_message(
            container, session_id=session_id, user_id=current_user.id, role="user", content=request.message, sequence_number=seq, attachments=request.attachments
        )
    except Exception as e:
        logger.error(f"Failed to persist user message: {str(e)}", exc_info=True)
        # We might not have seq if it failed early
        seq = 0


    async def generate_stream():
        full_response = ""
        input_tokens = count_tokens(request.message)
        
        try:
            async for chunk in azure_agent_service.stream_chat(request.message):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Error during LLM stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
            
        output_tokens = count_tokens(full_response)
        
        # Save assistant message now that response is complete
        try:
            await azure_cosmos_db_service.add_message(
                container, session_id=session_id, user_id=current_user.id, role="assistant", content=full_response, sequence_number=seq+1
            )
        except Exception as e:
            logger.error(f"Failed to persist assistant message: {str(e)}", exc_info=True)
            
        final_data = {
            "done": True,
            "response": full_response,
            "input_token": input_tokens,
            "output_token": output_tokens,
            "total_token": input_tokens + output_tokens,
            "session_id": str(session_id)
        }
        yield f"data: {json.dumps(final_data)}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


def _group_messages(messages):
    """
    Helper to group individual 'user' and 'assistant' messages into exchanges 
    keyed by the user message's UUID.
    """
    formatted = {}
    
    # Sort messages by sequence_number
    sorted_msgs = sorted(messages, key=lambda m: m.get("sequence_number", 0))
    
    current_user_msg = None
    for msg in sorted_msgs:
        msg_id_str = msg.get("id")
        # Legacy messages don't have IDs, so we generate one on the fly to group them
        msg_id = uuid.UUID(msg_id_str) if msg_id_str else uuid.uuid4()
        
        if msg.get("role") == "user":
            current_user_msg = msg
            current_user_msg["_temp_id"] = msg_id # Store it temporarily to link the assistant reply
            
            # Format datetime if available, otherwise just use current
            dt = msg.get("created_at")
            if dt:
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    dt = datetime.utcnow()
            else:
                dt = datetime.utcnow()

            formatted[msg_id] = MessageDetails(
                human_message=msg.get("content"),
                ai_message=None,
                created_at=dt
            )
        elif msg.get("role") == "assistant" and current_user_msg:
            # Attach to the current user message
            target_id = current_user_msg.get("_temp_id")
            if target_id in formatted:
                formatted[target_id].ai_message = msg.get("content")
            current_user_msg = None
            
    return formatted


@router.get("", response_model=AllSessionsResponse)
async def get_all_sessions(container: cosmos.ContainerProxy = Depends(get_db), current_user: User = Depends(validate_user)):
    """
    Retrieves all sessions (metadata only — no messages).
    Messages are loaded on-demand via GET /history/{session_id}.
    """
    logger.info(f"Retrieving all sessions for user {current_user.id}")
    all_sessions = await azure_cosmos_db_service.get_all_sessions(container, current_user.id)
            
    sessions_dict = {}
    for session in all_sessions:
        sessions_dict[uuid.UUID(session["id"])] = {
            "title": session.get("title", "New Chat"),
            "isPinned": session.get("is_pinned", False),
            "createdAt": session.get("created_at", datetime.utcnow().isoformat()),
        }
        
    return AllSessionsResponse(sessions=sessions_dict)


@router.get("/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: uuid.UUID, 
    container: cosmos.ContainerProxy = Depends(get_db), 
    current_user: User = Depends(validate_user)
):
    """
    Retrieves full chat history for a specific session ID.
    """
    session = await azure_cosmos_db_service.get_session(container, session_id, current_user.id)
    if not session:
        return SessionHistoryResponse(sessionId=session_id, messages={})
    
    # Get legacy embedded messages (if any from old sessions)
    legacy_messages = session.get("messages", [])
    
    # Get all standalone messages
    standalone_msgs = await azure_cosmos_db_service.get_messages_for_session(container, session_id, current_user.id)
    
    combined_messages = legacy_messages + standalone_msgs
    formatted_messages = _group_messages(combined_messages)
    
    return SessionHistoryResponse(
        sessionId=session_id,
        messages=formatted_messages
    )


@router.patch("/{session_id}/pin")
async def toggle_pin_session(
    session_id: uuid.UUID, 
    is_pinned: bool,
    container: cosmos.ContainerProxy = Depends(get_db), 
    current_user: User = Depends(validate_user)
):
    """
    Toggles the pinned status of a session.
    """
    session = await azure_cosmos_db_service.get_session(container, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session["is_pinned"] = is_pinned
    await container.replace_item(item=session["id"], body=session)
    return {"status": "success", "is_pinned": is_pinned}


@router.delete("/{session_id}")
async def delete_session(session_id: uuid.UUID, container: cosmos.ContainerProxy = Depends(get_db), current_user: User = Depends(validate_user)):
    """
    Deletes the conversation history for a specific session ID.
    """
    logger.info(f"Received request to delete session {session_id} from user {current_user.id}")
    deleted = await azure_cosmos_db_service.delete_session(container, session_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": f"Session {session_id} deleted successfully"}


@router.put("/{session_id}/messages/{message_id}")
async def update_message(
    session_id: uuid.UUID,
    message_id: uuid.UUID,
    update_data: ConversationMessageUpdate,
    container: cosmos.ContainerProxy = Depends(get_db),
    current_user: User = Depends(validate_user)
):
    """
    Updates the content of a specific message by its message ID.
    If a user message is updated, it re-runs the LLM and updates the corresponding assistant response, streaming the result.
    """
    content = update_data.human_message or update_data.ai_message
    if not content:
         raise HTTPException(status_code=400, detail="No content provided to update")
         
    updated_message = await azure_cosmos_db_service.update_message(
        container, 
        message_id, 
        content=content,
        user_id=current_user.id
    )
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    dt = datetime.utcnow()
    try:
        dt = datetime.fromisoformat(updated_message.get("created_at", ""))
    except Exception:
        pass

    # If an assistant message was edited, return the standard JSON response
    if updated_message.get("role") != "user":
        return ConversationMessageResponse(
            id=uuid.UUID(updated_message["id"]),
            session_id=uuid.UUID(updated_message["session_id"]),
            human_message="",
            ai_message=updated_message["content"],
            created_at=dt
        )

    # Otherwise, it's a user message: run LLM and stream the response
    async def generate_stream():
        full_response = ""
        
        try:
            async for chunk in azure_agent_service.stream_chat(content):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Error during LLM stream in update: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
            
        # We need to find the corresponding AI message and update its content
        try:
            seq = updated_message.get("sequence_number", 0)
            session_id_str = updated_message.get("session_id")
            query = "SELECT * FROM c WHERE c.type = 'message' AND c.session_id = @session_id AND c.sequence_number = @seq AND c.role = 'assistant'"
            parameters = [
                {"name": "@session_id", "value": session_id_str},
                {"name": "@seq", "value": seq + 1}
            ]
            
            ai_msg_to_update = None
            async for doc in container.query_items(query=query, parameters=parameters, partition_key=str(current_user.id)):
                ai_msg_to_update = doc
                break
                
            if ai_msg_to_update:
                ai_msg_to_update["content"] = full_response
                await container.replace_item(item=ai_msg_to_update["id"], body=ai_msg_to_update)
            else:
                await azure_cosmos_db_service.add_message(
                    container, session_id=session_id_str, user_id=current_user.id, role="assistant", content=full_response, sequence_number=seq+1
                )
        except Exception as e:
            logger.error(f"Failed to update corresponding AI message: {e}")

        final_data = {
            "done": True,
            "response": full_response,
            "humanMessage": content,
            "id": str(message_id)
        }
        yield f"data: {json.dumps(final_data)}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")
