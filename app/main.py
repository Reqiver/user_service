import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from fastapi.middleware.trustedhost import TrustedHostMiddleware


app = FastAPI()

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts
)


@app.get('/alive', status_code=200)
async def health_check():
    return {"Hello": "World"}


#app.include_router(<name_of_router>.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.running_port, reload=True)
