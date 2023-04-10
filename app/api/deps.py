from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def get_db() -> AsyncIOMotorClient:
    try:
        client = AsyncIOMotorClient(settings.mongo_uri)
        db = client[settings.db_name]
        yield db
    finally:
        client.close()
