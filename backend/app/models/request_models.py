from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str


class AgentRequest(BaseModel):
    message: str