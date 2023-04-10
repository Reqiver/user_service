from os import getenv
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "auth_service service"
    allowed_hosts: List[str] = ['localhost']
    running_port: int = 8000
    testing: bool = getenv('TESTING')

    access_token_expires_in: int = 15
    refresh_token_expires_in: int = 60 * 24
    jwt_algorithm: str = 'HS256'
    jwt_secret_key: str
    jwt_secret_refresh_key: str

    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    mongo_initdb_database: str
    mongo_initdb_host: str = 'db'
    mongo_initdb_port: int = 27017

    @property
    def db_name(self) -> str:
        db_name = self.mongo_initdb_database
        if self.testing:
            db_name = f'{self.mongo_initdb_database}_test'
        return db_name

    @property
    def mongo_uri(self) -> str:
        return f"mongodb://{self.mongo_initdb_root_username}:{self.mongo_initdb_root_password}@{self.mongo_initdb_host}:{self.mongo_initdb_port}/{self.db_name}?authSource={self.mongo_initdb_root_username}"

    class Config:
        env_file = ".env"


settings = Settings()
