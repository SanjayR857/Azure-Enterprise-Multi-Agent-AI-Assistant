from datetime import datetime
import uuid

from sqlalchemy import (
    Column, String, DateTime, Integer, Boolean, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    model_name = Column(String(100), nullable=False, default="gpt-4o")
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.sequence_number")
