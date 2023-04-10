import os

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

# This sets `os.environ`,
# If we placed it below the application import, it would raise an error
# informing us that 'TESTING' had already been read from the environment.
os.environ['TESTING'] = 'True'

from app.config import settings


@pytest.fixture(scope="function")
def test_db():
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    yield db
    client = AsyncIOMotorClient(settings.mongo_uri)
    client.drop_database(settings.db_name)
