from pydantic import BaseModel, EmailStr
from enum import Enum


class SexEnum(str, Enum):
    male: str = "мужской"
    female: str = "женский"


class UserModel(BaseModel):
    name: str
    surname: str
    sex: SexEnum
    email: EmailStr
    avatar: bytes
