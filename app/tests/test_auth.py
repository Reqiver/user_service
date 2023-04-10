from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app import crud, schemas
from app.tests.utils import test_user_create
from app.utils.user_utils import get_hashed_password, create_access_token

client = TestClient(app)
pytest_plugins = ('pytest_asyncio',)


def create_user_raw():
    raw_user = test_user_create.copy()
    raw_user['hashed_pass'] = get_hashed_password(raw_user.pop('password'))
    raw_user['id'] = str(uuid4())
    return raw_user


@pytest.mark.asyncio
async def test_unauthorized_user(test_db: AsyncIOMotorClient):
    users_collection = test_db["users"]
    raw_user = create_user_raw()
    await crud.user.create(schemas.CreateUser(**raw_user), users_collection)

    response = client.get("/users/profile")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_authorized_user(test_db: AsyncIOMotorClient):
    users_collection = test_db["users"]
    raw_user = create_user_raw()
    await crud.user.create(schemas.CreateUser(**raw_user), users_collection)
    token = create_access_token(raw_user['id'])

    response = client.get("/users/profile", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["id"] == raw_user["id"]
