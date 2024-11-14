from typing import Any, Annotated

from fastapi import APIRouter, Depends

from ..deps import SessionDep
from ... import crud
from ...models import ClientCreate

router = APIRouter()


@router.post("/create")
async def register_client(*, session: SessionDep, client: Annotated[ClientCreate, Depends()]) -> Any:
    """
    Create new client
    :param session: SessionDep - сессия базы данных для выполнения операций с базой данных.
    :param client: ClientCreate - объект, содержащий данные для создания нового клиента.
    :return:
    """
    client = await crud.create_client(session=session, client_create=client)
    return {"status_code": 200}
