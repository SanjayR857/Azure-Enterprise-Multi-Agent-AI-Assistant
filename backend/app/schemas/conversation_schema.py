from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

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
    human_message: str = Field(..., alias="humanMessage")
    ai_message: str | None = Field(None, alias="aiMessage")
    created_at: datetime = Field(..., alias="createdAt")

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

class SessionDetails(BaseModel):
    title: str = Field(...)
    is_pinned: bool = Field(False)
    messages: dict[UUID, MessageDetails] = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
    )

class AllSessionsHistoryResponse(BaseModel):
    sessions: dict[UUID, SessionDetails] = Field(..., description="Dictionary mapping session ID to its details")

    model_config = ConfigDict(
        populate_by_name=True,
    )
