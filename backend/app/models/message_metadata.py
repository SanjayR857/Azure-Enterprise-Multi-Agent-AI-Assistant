from datetime import datetime
import uuid

from sqlalchemy import (
    Column, String, DateTime, Integer
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class MessageMetadata(Base):
    __tablename__ = "message_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    tokens_prompt = Column(Integer, default=0)
    tokens_completion = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)
    
    latency_ms = Column(Integer, nullable=True)
    finish_reason = Column(String(50), nullable=True)
    
    # Store any extra tool calls or arbitrary json
    extra_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationship back to message
    message = relationship("Message", back_populates="meta_info", uselist=False)
