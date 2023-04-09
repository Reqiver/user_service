from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status
from starlette.authentication import requires
from starlette.requests import Request

from app import crud, schemas
from app.api import deps

from app.utils.user_utils import get_hashed_password, authenticate_user, create_access_token, \
    create_refresh_token, refresh_token_helper

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    "/profile/",
    response_model=schemas.RetrieveUser,
    description="Retrieve profile of authorized user.",
)
@requires('authenticated')
async def get_authorized_user(request: Request, db: AsyncIOMotorClient = Depends(deps.get_db)):
    users_collection = db["users"]
    user = await crud.user.get(request.user.id, users_collection)
    return user


@router.get(
    "/{user_id}/",
    response_model=schemas.RetrieveUser,
    description="Retrieve profile by user ID.",
)
async def get_user_by_id(user_id: str, db: AsyncIOMotorClient = Depends(deps.get_db)):
    users_collection = db["users"]
    user = await crud.user.get(user_id, users_collection)
    return user


@router.get(
    "/",
    response_model=List[schemas.RetrieveUser],
    description="Retrieve list of users.",
)
async def get_users(skip: int = 0, limit: int = 12, db: AsyncIOMotorClient = Depends(deps.get_db)):
    users_collection = db["users"]
    users = await crud.user.get_multi(users_collection, skip=skip, limit=limit)
    return users


@router.post(
    "/",
    status_code=201,
    response_model=schemas.RetrieveUser,
    description="Create user.",
)
async def create_user(
        user: schemas.CreateUserRequest,
        db: AsyncIOMotorClient = Depends(deps.get_db),
):
    users_collection = db["users"]
    raw_user = user.dict()
    raw_user['hashed_pass'] = get_hashed_password(raw_user.pop('password'))
    raw_user['id'] = str(uuid4())
    user_obj = schemas.CreateUser(**raw_user)
    created_user = await crud.user.create(user_obj, users_collection)
    return created_user


@router.patch(
    "/",
    response_model=schemas.RetrieveUser,
    description="Edit profile of authorized user",
)
@requires('authenticated')
async def update_authorized_user(
        data_to_update: schemas.UpdateUserRequest,
        request: Request,
        db: AsyncIOMotorClient = Depends(deps.get_db),
):
    users_collection = db["users"]
    raw_user = data_to_update.dict(exclude_unset=True)
    if password := raw_user.pop('password', None):
        raw_user['hashed_pass'] = get_hashed_password(password)
    user_obj = schemas.UpdateUser(**raw_user)
    created_user = await crud.user.update(request.user.id, user_obj, users_collection)
    return created_user


@router.patch(
    "/{user_id}/",
    response_model=schemas.RetrieveUser,
    description="Edit user's profile by ID. Usage is allowed only for Admin role.",
)
@requires(['authenticated', 'admin'])
async def update_user_by_id(
        user_id: str,
        data_to_update: schemas.BaseUpdateUser,
        request: Request,
        db: AsyncIOMotorClient = Depends(deps.get_db),
):
    users_collection = db["users"]
    created_user = await crud.user.update(user_id, data_to_update, users_collection)
    return created_user


@router.post(
    "/token",
    response_model=schemas.TokenSchema,
    description="Retrieve authorization tokens. Common JWT auth flow.",
)
async def login(
    login_data: schemas.LoginUser,
    db: AsyncIOMotorClient = Depends(deps.get_db),
):
    users_collection = db["users"]
    user = await authenticate_user(login_data.id, login_data.password, users_collection)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post(
    "/refresh_token",
    response_model=schemas.TokenSchema,
    description="Refresh access_token token with refresh_token. Common JWT auth flow.",
)
async def get_new_token_with_refresh_token(
    r_token: schemas.RefreshTokenSchema,
    db: AsyncIOMotorClient = Depends(deps.get_db),
):
    users_collection = db["users"]
    return await refresh_token_helper(r_token.refresh_token, users_collection)


@router.delete(
    "/",
    status_code=204,
    description="Remove authorized user.",
)
@requires('authenticated')
async def remove_authorized_user(
        request: Request,
        db: AsyncIOMotorClient = Depends(deps.get_db),
):
    users_collection = db["users"]
    await crud.user.remove(request.user.id, users_collection)
    return
