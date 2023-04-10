import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app import crud, schemas
from app.tests.utils import test_user_create

client = TestClient(app)
pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_create_user(test_db: AsyncIOMotorClient):
    test_user = schemas.CreateUserRequest(**test_user_create)

    response = client.post("/users", json=test_user.dict(exclude_unset=True))

    assert response.status_code == 201, response.json()

    # Check that the response body matches the expected schema
    created_user = schemas.RetrieveUser(**response.json())
    assert created_user.first_name == test_user.first_name
    assert created_user.last_name == test_user.last_name
    assert created_user.role == test_user.role
    assert created_user.is_active
    assert created_user.created_at is not None
    assert created_user.last_login is not None

    # Check that the user was actually created in the database
    users_collection = test_db["users"]
    db_user = await crud.user.get(created_user.id, users_collection)
    assert db_user is not None
    assert db_user.first_name == created_user.first_name
    assert db_user.last_name == created_user.last_name
    assert db_user.role == created_user.role
    assert db_user.is_active
    assert db_user.created_at is not None
    assert db_user.last_login is not None
    db_users = await crud.user.get_multi(users_collection)
    assert len(db_users) == 1
