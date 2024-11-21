import uuid
from typing import Optional

from fastapi import UploadFile
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from .utils import SexEnum


class ClientBase(SQLModel):
    name: Optional[str] = Field(default=None, max_length=55)
    surname: Optional[str] = Field(default=None, max_length=55)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    sex: Optional[SexEnum] = Field(default=None)
    is_active: bool = True
    is_superuser: bool = False


class ClientUpdateLocation(SQLModel):
    latitude: float
    longitude: float


class LikeBase(SQLModel):
    liker_id: uuid.UUID
    liked_id: uuid.UUID
    match: bool = False


class FilterClient(SQLModel):
    sex: Optional[SexEnum] = Field(default=None)
    name: Optional[str] = Field(default=None, max_length=55)
    surname: Optional[str] = Field(default=None, max_length=55)
    distance: Optional[float] = Field(default=None)


class ClientCreate(ClientBase):
    password: str = Field(min_length=8, max_length=40)
    avatar: Optional[UploadFile] = Field(default=None)


class Client(ClientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    avatar: Optional[bytes] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)


class Like(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    liker_id: uuid.UUID
    liked_id: uuid.UUID
    match: bool = False


class LikePublic(LikeBase):
    pass


class ClientPublic(ClientBase):
    id: uuid.UUID


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None
