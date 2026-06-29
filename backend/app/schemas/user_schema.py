from pydantic import BaseModel
import uuid
from datetime import datetime

class User(BaseModel):
    id: uuid.UUID
    azure_oid: str
    email: str
    name: str
    created_at: datetime
