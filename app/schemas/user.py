from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator, Field

from app.utils.user_utils import password_validation


class UserRole(str, Enum):
    admin = 'admin'
    dev = 'dev'
    simple_mortal = 'simple mortal'


class BaseUser(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=24, description="first name")
    last_name: str = Field(..., min_length=2, max_length=24, description="last name")
    role: UserRole = UserRole.simple_mortal

    class Config:
        orm_mode = True


class RetrieveUser(BaseUser):
    id: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class RetrieveUserWithPass(RetrieveUser):
    hashed_pass: str


class CreateUserRequest(BaseUser):
    password: str = Field(
        ...,
        min_length=5,
        max_length=24,
        description="User password. Must be between 5 and 24 characters, "
                    "and contain at least one letter and one digit.",
    )

    @validator('password')
    def password_validation(cls, value):
        return password_validation(value)


class CreateUser(BaseUser):
    id: str
    is_active: bool = True
    created_at: Optional[datetime] = datetime.now()
    last_login: Optional[datetime] = datetime.now()
    hashed_pass: str


class LoginUser(BaseModel):
    id: str
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class BaseUpdateUser(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[bool]

    @validator('first_name')
    def first_name_validation(cls, value):
        if len(value) < 2 or len(value) > 24:
            raise ValueError('First name must be between 5 and 24 characters')
        return value

    @validator('last_name')
    def last_name_validation(cls, value):
        if len(value) < 2 or len(value) > 24:
            raise ValueError('Last name must be between 5 and 24 characters')
        return value

    class Config:
        orm_mode = True


class UpdateUserRequest(BaseUpdateUser):
    password: Optional[str]

    @validator('password')
    def password_validation(cls, value):
        if len(value) < 5 or len(value) > 24:
            raise ValueError('Password must be between 5 and 24 characters')
        return password_validation(value)


class UpdateUser(BaseUpdateUser):
    hashed_pass: Optional[str]
