from pydantic import BaseModel
import uuid

class ChatRequest(BaseModel):
    message: str

class AgentRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None