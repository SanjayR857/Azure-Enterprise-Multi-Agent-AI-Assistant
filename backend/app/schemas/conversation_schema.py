from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

class AgentRequest(BaseModel):
    session_id: UUID | None = Field(None, alias="sessionId")
    message: str

    model_config = ConfigDict(
        populate_by_name=True,
    )

class ConversationMessageCreate(BaseModel):
    session_id: UUID = Field(..., alias="sessionId")
    human_message: str = Field(..., alias="humanMessage")
    ai_message: str | None = Field(None, alias="aiMessage")

    model_config = ConfigDict(
        populate_by_name=True,
    )

class ConversationMessageResponse(BaseModel):
    id: UUID = Field(..., description="Message ID")
    session_id: UUID = Field(..., alias="sessionId")
    human_message: str = Field(..., alias="humanMessage")
    ai_message: str | None = Field(None, alias="aiMessage")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class ConversationMessageUpdate(BaseModel):
    human_message: str | None = Field(None, alias="humanMessage", description="Updated human message")
    ai_message: str | None = Field(None, alias="aiMessage", description="Updated AI message")


class MessageDetails(BaseModel):
    human_message: str = Field(..., validation_alias="humanMessage", serialization_alias="humanMessage")
    ai_message: str | None = Field(None, validation_alias="aiMessage", serialization_alias="aiMessage")
    created_at: datetime = Field(..., validation_alias="createdAt", serialization_alias="createdAt")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class SessionHistoryResponse(BaseModel):
    session_id: UUID = Field(..., alias="sessionId")
    messages: dict[UUID, MessageDetails] = Field(..., description="Dictionary mapping message ID to message details")

    model_config = ConfigDict(
        populate_by_name=True,
    )

class PaginatedSessionHistoryResponse(BaseModel):
    session_id: UUID = Field(..., alias="sessionId")
    messages: dict[UUID, MessageDetails] = Field(..., description="Dictionary mapping message ID to message details")
    total_messages: int = Field(..., alias="totalMessages", description="Total number of messages in this session")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Current offset")
    has_more: bool = Field(..., alias="hasMore", description="Whether more messages exist beyond this page")

    model_config = ConfigDict(
        populate_by_name=True,
    )

class SessionDetails(BaseModel):
    """Metadata for a single chat session (no messages)."""
    title: str = Field(..., description="Auto-generated or user-provided session title")
    is_pinned: bool = Field(False, alias="isPinned", description="Whether the session is pinned to the top")
    created_at: datetime = Field(..., alias="createdAt", description="Session creation timestamp")

    model_config = ConfigDict(
        populate_by_name=True,
    )

class AllSessionsResponse(BaseModel):
    """Response containing all session metadata for the current user."""
    sessions: dict[UUID, SessionDetails] = Field(
        default_factory=dict,
        description="Dictionary mapping session ID to its metadata"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )
