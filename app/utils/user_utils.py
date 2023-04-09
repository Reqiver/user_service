import re
from datetime import datetime, timedelta

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from starlette import status

from app import crud, schemas
from app.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def password_validation(password):
    if not re.search(r'\w', password):
        raise ValueError('Password must contain at least one letter')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')

    return password


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(uuid: str) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=settings.access_token_expires_in)

    to_encode = {"exp": expires_delta, "sub": uuid}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(uuid: str) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expires_in)

    to_encode = {"exp": expires_delta, "sub": uuid}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_refresh_key, settings.jwt_algorithm)
    return encoded_jwt


async def authenticate_user(uuid: str, password: str, coll: AsyncIOMotorCollection):
    user = await crud.user.get_with_hash_pass(uuid, coll)
    if not user:
        return False
    if not verify_password(password, user.hashed_pass):
        return False
    return user


async def refresh_token_helper(r_token: str, coll: AsyncIOMotorCollection):
    try:
        payload = jwt.decode(
            r_token, settings.jwt_secret_refresh_key, algorithms=[settings.jwt_algorithm],
        )
        token_data = schemas.TokenPayload(**payload)
        if token_data.sub is None or datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await crud.user.get(token_data.sub, coll)
    if user is None:
        raise credentials_exception

    access_token = create_access_token(token_data.sub)
    return {"access_token": access_token, "refresh_token": r_token}


async def get_current_user(token: str):
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm],
        )
        token_data = schemas.TokenPayload(**payload)
        if token_data.sub is None or datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_initdb_database]
    coll = db['users']
    user = await crud.user.get(token_data.sub, coll)

    if user is None:
        raise credentials_exception
    return user
