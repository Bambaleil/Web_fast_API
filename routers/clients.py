from typing import Annotated
from passlib.context import CryptContext

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from models.clientsmodel import ClientsModelAdd, add_watermark_with_photo

router = APIRouter(
    prefix="/api/clients",
    tags=["Клиенты"]
)

clients = []

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/create")
async def create_clients(client: Annotated[ClientsModelAdd, Depends()]):
    clients.append(client)
    watermarked_image: bytes = await add_watermark_with_photo(client.avatar.file.read(), opacity=0.1)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(client.password)
    return {"status_code": 200}
