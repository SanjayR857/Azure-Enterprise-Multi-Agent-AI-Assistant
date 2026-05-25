from pydantic import BaseModel

class RequestModel(BaseModel):
    response: str