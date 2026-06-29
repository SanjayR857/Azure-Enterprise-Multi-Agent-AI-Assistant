import asyncio
from app.database.session import init_db

async def reset_db():
    print("Initializing Cosmos DB NoSQL Database and Container...")
    await init_db()
    print("Database initialization complete.")

if __name__ == "__main__":
    asyncio.run(reset_db())
