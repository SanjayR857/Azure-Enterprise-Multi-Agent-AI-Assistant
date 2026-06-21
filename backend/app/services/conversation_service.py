import logging
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.models.chat_session import ChatSession
from app.models.message import Message

logger = logging.getLogger(__name__)

class ConversationService:
    """
    Service class handling operations related to conversation history persistence and retrieval
    using the new relational models.
    """

    async def create_session(self, db: AsyncSession, user_id: uuid.UUID, session_id: uuid.UUID = None, title: str = None) -> ChatSession:
        try:
            db_session = ChatSession(
                id=session_id or uuid.uuid4(),
                user_id=user_id,
                title=title
            )
            db.add(db_session)
            await db.commit()
            await db.refresh(db_session)
            return db_session
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create chat session: {str(e)}")
            raise e

    async def get_session(self, db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        try:
            stmt = select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).options(selectinload(ChatSession.messages))
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get chat session: {str(e)}")
            raise e

    async def get_all_sessions(self, db: AsyncSession, user_id: uuid.UUID) -> list[ChatSession]:
        try:
            stmt = select(ChatSession).where(ChatSession.user_id == user_id).options(selectinload(ChatSession.messages)).order_by(ChatSession.created_at.desc())
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve all sessions: {str(e)}")
            return []

    async def add_message(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        role: str, 
        content: str, 
        sequence_number: int
    ) -> Message:
        try:
            db_message = Message(
                session_id=session_id,
                role=role,
                content=content,
                sequence_number=sequence_number
            )
            db.add(db_message)
            await db.commit()
            await db.refresh(db_message)
            return db_message
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to add message to database: {str(e)}")
            raise e

    async def delete_session(self, db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        try:
            stmt = delete(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            raise e

    async def delete_message(self, db: AsyncSession, message_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        try:
            stmt = select(Message).join(ChatSession).where(
                Message.id == message_id, 
                ChatSession.user_id == user_id
            )
            result = await db.execute(stmt)
            message = result.scalar_one_or_none()
            if not message:
                return False
            
            await db.delete(message)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to delete message {message_id}: {str(e)}")
            raise e

    async def update_message(
        self, 
        db: AsyncSession, 
        message_id: uuid.UUID, 
        content: str,
        user_id: uuid.UUID
    ) -> Message | None:
        try:
            stmt = select(Message).join(ChatSession).where(
                Message.id == message_id,
                ChatSession.user_id == user_id
            )
            result = await db.execute(stmt)
            db_message = result.scalar_one_or_none()
            if db_message:
                db_message.content = content
                await db.commit()
                await db.refresh(db_message)
            return db_message
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to update message {message_id}: {str(e)}")
            raise e

conversation_service = ConversationService()
