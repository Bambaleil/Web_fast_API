from typing import Annotated

from fastapi import APIRouter, Depends

from models.clientsmodel import ClientsModelAdd

router = APIRouter(
    prefix="/api/clients",
    tags=["Клиенты"]
)

clients = []


@router.post("/create")
async def create_clients(client: Annotated[ClientsModelAdd, Depends()]):
    clients.append(client)
    return {"status_code": 200}
