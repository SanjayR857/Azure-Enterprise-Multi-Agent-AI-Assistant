# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from app.services.agent_service import agent_service
from app.utils import count_tokens
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.conversation_service import conversation_service
from app.schemas.request_models import AgentRequest
from app.schemas.response_models import AgentResponse

from app.schemas.conversation_schema import (
    ConversationMessageCreate,
    ConversationMessageUpdate,
    ConversationMessageResponse,
    SessionHistoryResponse,
    AllSessionsHistoryResponse,
    MessageDetails
)

import uuid

import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversation",
    tags=["conversation"],
)

@router.post("/agent", response_model=AgentResponse)
async def conversation(request: AgentRequest, db: AsyncSession = Depends(get_db)):
    """
    Handles incoming user messages, triggers the agent orchestrator, 
    persists the exchange to the conversation history, and returns the response.
    """
    # 1. Run the blocking orchestrator workflow in a thread pool
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, agent_service.run_orchestrator, request.message)
    
    # 2. Track token counts
    input_tokens = count_tokens(request.message)
    output_tokens = count_tokens(response)
    
    # 3. Determine/generate session ID
    session_id = request.session_id or uuid.uuid4()
    
    # 4. Asynchronously persist the conversation message exchange to database
    try:
        session = await conversation_service.get_session(db, session_id)
        if not session:
            # Dummy user UUID for now since no auth
            user_id = uuid.UUID(int=0)
            session = await conversation_service.create_session(db, user_id=user_id, session_id=session_id, title=request.message[:50])
            # New session has no messages yet, so sequence starts at 0
            seq = 0
        else:
            # Existing session: messages are eagerly loaded via selectinload in get_session
            seq = len(session.messages) if session.messages else 0
        
        # Save user message
        user_msg = await conversation_service.add_message(
            db, session_id=session_id, role="user", content=request.message, sequence_number=seq
        )
        
        # Save assistant message
        ai_msg = await conversation_service.add_message(
            db, session_id=session_id, role="assistant", content=response, sequence_number=seq+1
        )
    except Exception as e:
        logger.error(f"Failed to persist conversation history: {str(e)}", exc_info=True)

    return AgentResponse(
        input_token=input_tokens,
        output_token=output_tokens,
        total_token=input_tokens + output_tokens,
        response=response,
        session_id=session_id
    )

def _group_messages(messages):
    """
    Helper to group individual 'user' and 'assistant' messages into exchanges 
    keyed by the user message's UUID.
    """
    formatted = {}
    
    # Sort messages by sequence_number
    sorted_msgs = sorted(messages, key=lambda m: m.sequence_number)
    
    current_user_msg = None
    for msg in sorted_msgs:
        if msg.role == "user":
            current_user_msg = msg
            formatted[msg.id] = MessageDetails(
                humanMessage=msg.content,
                aiMessage=None,
                createdAt=msg.created_at
            )
        elif msg.role == "assistant" and current_user_msg:
            # Attach to the current user message
            formatted[current_user_msg.id].ai_message = msg.content
            current_user_msg = None
            
    return formatted

@router.get("/all_sessions", response_model=AllSessionsHistoryResponse)
async def get_all_sessions(db: AsyncSession = Depends(get_db)):
    """
    Retrieves all sessions with their complete message history.
    """
    all_sessions = await conversation_service.get_all_sessions(db)
    
    sessions_dict = {}
    for session in all_sessions:
        sessions_dict[session.id] = _group_messages(session.messages)
        
    return AllSessionsHistoryResponse(sessions=sessions_dict)

@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
async def get_history(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieves the complete chat history for a specific session ID structured by message ID.
    """
    session = await conversation_service.get_session(db, session_id)
    if not session:
        return SessionHistoryResponse(sessionId=session_id, messages={})
        
    formatted_messages = _group_messages(session.messages)
        
    return SessionHistoryResponse(
        sessionId=session_id,
        messages=formatted_messages
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Deletes the conversation history for a specific session ID.
    """
    deleted = await conversation_service.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": f"Session {session_id} deleted successfully"}

@router.delete("/message/{message_id}")
async def delete_message(message_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Deletes a specific message by its message ID. 
    """
    deleted = await conversation_service.delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success", "message": f"Message {message_id} deleted successfully"}

@router.put("/message/{message_id}", response_model=ConversationMessageResponse)
async def update_message(
    message_id: uuid.UUID,
    update_data: ConversationMessageUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates the content of a specific message by its message ID.
    """
    content = update_data.human_message or update_data.ai_message
    if not content:
         raise HTTPException(status_code=400, detail="No content provided to update")
         
    updated_message = await conversation_service.update_message(
        db, 
        message_id, 
        content=content
    )
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    return ConversationMessageResponse(
        id=updated_message.id,
        sessionId=updated_message.session_id,
        humanMessage=updated_message.content if updated_message.role == "user" else "",
        aiMessage=updated_message.content if updated_message.role == "assistant" else "",
        createdAt=updated_message.created_at
    )
