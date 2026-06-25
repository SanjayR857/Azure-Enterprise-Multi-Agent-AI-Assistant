from datetime import datetime
import uuid

from sqlalchemy import (
    Column, String, DateTime, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(255), nullable=False)
    
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="documents")
    session = relationship("ChatSession", backref="documents")


    


    
    