from datetime import datetime
import uuid

from sqlalchemy import (
    Column, String, DateTime, Integer, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(50), nullable=False) # e.g., 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    
    sequence_number = Column(Integer, nullable=False) # To maintain exact ordering
    
    metadata_id = Column(UUID(as_uuid=True), ForeignKey("message_metadata.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    meta_info = relationship("MessageMetadata", back_populates="message", uselist=False)
