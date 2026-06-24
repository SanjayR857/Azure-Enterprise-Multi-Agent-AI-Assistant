from datetime import datetime
import uuid

from sqlalchemy import (
    Column, Strnig, DateTime, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Document(Base):
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = 