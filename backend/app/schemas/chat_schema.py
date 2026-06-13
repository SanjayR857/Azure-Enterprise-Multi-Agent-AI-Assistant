from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class chatMessageCreate(BaseModel):
    session_id: UUID = Field(..., alias="sessionId")
    role: str = Field(..., description="User, Agent, or System")
    content: str = Field(..., description="Message content")
    

class chatMessageResponse(chatMessageCreate):
    
    id: UUID = Field(..., description="Message ID")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )