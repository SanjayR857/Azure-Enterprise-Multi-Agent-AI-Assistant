from pydantic import BaseModel
import uuid

class RequestModel(BaseModel):
    input_token: int
    output_token: int
    total_token: int
    response: str

class AgentResponse(BaseModel):
    input_token: int
    output_token: int
    total_token: int
    response: str
    session_id: uuid.UUID | None = None