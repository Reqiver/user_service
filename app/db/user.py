from motor.motor_asyncio import AsyncIOMotorClient


async def create_user_index(db: AsyncIOMotorClient):

    users_collection = db['users']
    await users_collection.create_index('id', unique=True)
