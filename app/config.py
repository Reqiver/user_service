from os import getenv
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "auth_service service"
    allowed_hosts: List[str] = ['localhost']
    running_port: int = 8000
    testing: bool = getenv('TESTING')

    access_token_expires_in: int = 15
    refresh_token_expires_in: int = 60
    jwt_algorithm: str = 'RS256'

    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    mongo_initdb_database: str
    mongo_initdb_port: int = 27017

    class Config:
        env_file = ".env"


settings = Settings()
