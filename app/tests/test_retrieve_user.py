from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app import crud, schemas
from app.main import app
from app.tests.utils import test_user

client = TestClient(app)


def test_get_users():
    test_user2 = test_user.copy()
    test_user2["first_name"] = "John"
    test_user2["last_name"] = "Doe"
    test_user2["id"] = "91dba2e3-d98d-4abe-ab66-162d2398e178"
    mock_response = [schemas.RetrieveUser(**test_user), schemas.RetrieveUser(**test_user2)]

    with patch.object(crud.user, "get_multi", new=AsyncMock(return_value=mock_response)):

        response = client.get("/users")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        assert isinstance(users[0]["id"], str)
        assert isinstance(users[0]["created_at"], str)
        assert isinstance(users[0]["last_login"], str)
        assert users[0]["first_name"] == test_user["first_name"]
        assert users[0]["last_name"] == test_user["last_name"]
        assert users[0]["role"] == test_user["role"]
        assert users[0]["is_active"] is True
        assert users[0]["id"] == test_user['id']
        assert users[1]["id"] == test_user2['id']


def test_get_user_by_id():
    with patch.object(crud.user, "get",
                      new=AsyncMock(return_value=schemas.RetrieveUser(**test_user))):
        response = client.get(f"/users/{test_user['id']}")
        assert response.status_code == 200
        user = response.json()
        assert user['id'] == test_user['id']
