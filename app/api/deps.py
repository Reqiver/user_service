from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def get_db() -> AsyncIOMotorClient:
    try:
        client = AsyncIOMotorClient(settings.mongo_uri)
        db = client[settings.mongo_initdb_database]
        yield db
    finally:
        client.close()
