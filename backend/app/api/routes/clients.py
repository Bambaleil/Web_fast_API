import uuid
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Sequence

from ..deps import SessionDep, CurrentClient
from app.models import (ClientCreate,
                        ClientPublic,
                        Client,
                        FilterClient,
                        ClientUpdateLocation)
from ... import crud
from ...utils import add_watermark_with_photo

router = APIRouter()


@router.post("/create", response_model=ClientPublic)
async def create_client(*, session: SessionDep,
                        client_in: Annotated[ClientCreate, Depends()]
                        ) -> Optional[Client]:
    """
    Create new client

    :param session: SessionDep - сессия базы данных
     для выполнения операций с базой данных.
    :param client_in: Annotated[ClientCreate, Depends()] -
    объект, содержащий данные для создания нового клиента.
    :return: Client
    """
    client: Optional[Client] = await crud.get_client_by_email(
        session=session,
        email=client_in.email
    )
    if client:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    if client_in.avatar:
        if client_in.avatar.size > 1024 * 1024 * 5:
            raise HTTPException(
                status_code=400,
                detail="The file size is over 5 MB")
        if not client_in.avatar.content_type.startswith("image"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type")
        avatar_bytes = await client_in.avatar.read()
        avatar_with_watermark = await add_watermark_with_photo(
            avatar=avatar_bytes
        )
        client_in.avatar = avatar_with_watermark
    client: Client = await crud.create_client(
        session=session,
        client_create=client_in)
    return client


@router.get("/list", response_model=List[ClientPublic])
async def filter_list_client(current_client: CurrentClient,
                             session: SessionDep,
                             filter_client: Annotated[FilterClient, Depends()]
                             ) -> Sequence[Optional[Client]]:
    clients: Sequence[Optional[Client]] = await (
        crud.get_list_filter_client(session=session,
                                    current_client=current_client,
                                    filter_client=filter_client))
    return clients


@router.get("/match/{client_id}")
async def get_list_match(client_id: uuid.UUID, session: SessionDep) -> None:
    db_client: Client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(
            status_code=400,
            detail="The liker with this ID does not exist in the system."
        )


@router.patch("/location/{client_id}", response_model=ClientPublic)
async def update_location_client(
        client_id: uuid.UUID, session: SessionDep,
        coordinate: Annotated[ClientUpdateLocation, Depends()]) -> Client:
    db_client: Client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(
            status_code=400,
            detail="The liker with this ID does not exist in the system."
        )
    client: Client = await crud.update_client(
        session=session,
        db_client=db_client,
        client_up=coordinate
    )
    return client
