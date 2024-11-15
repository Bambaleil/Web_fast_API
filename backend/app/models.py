import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field

from .utils import SexEnum


class ClientBase(SQLModel):
    name: Optional[str] = Field(default=None, max_length=55)
    surname: Optional[str] = Field(default=None, max_length=55)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    sex: Optional[SexEnum] = Field(default=None)
    is_active: bool = True
    is_superuser: bool = False


class ClientCreate(ClientBase):
    password: str = Field(min_length=8, max_length=40)


class ClientRegister(ClientBase):
    avatar: UploadFile = Field()

    @field_validator('avatar', mode='before')
    def validate_avatar(cls, value):
        if not value:
            return value

        if value.size > 1024 * 1024 * 5:
            raise HTTPException(status_code=416, detail="The file size is over 5 MB")

        if not value.content_type.startswith("image"):
            raise HTTPException(status_code=415, detail="Invalid file type")

        return value


class Client(ClientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    avatar: Optional[bytes] = Field(default=None)


class ClientPublic(ClientBase):
    id: uuid.UUID
