import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.user import create_user_index
from app.api.routers import users

from app.config import settings
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.utils.middlewares import JWTAuthenticationMiddleware

app = FastAPI()

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts
)
app.add_middleware(JWTAuthenticationMiddleware)


@app.get('/alive', status_code=200)
async def health_check():
    return {"Hello": "World"}


@app.on_event("startup")
async def startup():
    client = AsyncIOMotorClient(settings.mongo_uri)
    database = client[settings.mongo_initdb_database]

    await create_user_index(database)
    client.close()


app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.running_port, reload=True)
