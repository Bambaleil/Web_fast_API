import uuid
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Sequence

from ..deps import SessionDep
from ... import crud
from ...crud import get_list_filter_client
from ...models import ClientCreate, ClientPublic, Client, FilterClient

router = APIRouter()


@router.post("/create", response_model=ClientPublic)
async def register_client(*, session: SessionDep, client_in: Annotated[ClientCreate, Depends()]) -> Optional[Client]:
    """
    Create new client
    :param session: SessionDep - сессия базы данных для выполнения операций с базой данных.
    :param client_in: Annotated[ClientCreate, Depends()] - объект, содержащий данные для создания нового клиента.
    :return: Client
    """
    client: Optional[Client] = await crud.get_client_by_email(session=session, email=client_in.email)
    if client:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    client: Client = await crud.create_client(session=session, client_create=client_in)
    return client


@router.get("/list", response_model=List[ClientPublic])
async def filter_list_client(session: SessionDep, filter_client: Annotated[FilterClient, Depends()]):
    clients: Sequence[Optional[Client]] = await get_list_filter_client(session=session, filter_client=filter_client)
    return clients


@router.get("/{client_id}/match")
async def get_list_match(client_id: uuid.UUID, session: SessionDep):
    client: Client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=400,
            detail="The liker with this ID does not exist in the system."
        )
