import asyncio
from app.database.session import engine
from sqlalchemy import text

async def alter():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE"))
    print("Added is_pinned to chat_sessions table")

if __name__ == "__main__":
    asyncio.run(alter())
