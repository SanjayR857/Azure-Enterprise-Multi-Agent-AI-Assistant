import asyncio
from app.database.session import engine
from app.models import Base
from sqlalchemy import text

async def reset_db():
    print("Dropping existing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # Drop old tables that might not be in Base
        await conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS conversation_history CASCADE"))
        
        print("Re-creating tables with the new schema...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database reset successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_db())
