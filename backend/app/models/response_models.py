from pydantic import BaseModel

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