from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException

from ..deps import SessionDep
from ... import crud
from ...models import ClientCreate, ClientPublic

router = APIRouter()


@router.post("/create", response_model=ClientPublic)
async def register_client(*, session: SessionDep, client_in: Annotated[ClientCreate, Depends()]) -> Any:
    """
    Create new client
    :param session: SessionDep - сессия базы данных для выполнения операций с базой данных.
    :param client_in: Annotated[ClientCreate, Depends()] - объект, содержащий данные для создания нового клиента.
    :return:
    """
    client = await crud.get_client_by_email(session=session, email=client_in.email)
    if client:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    client = await crud.create_client(session=session, client_create=client_in)
    # if settings.emails_enabled and client_in.email:
    #     email_data = generate_new_account_email(
    #         email_to=client_in.email, client_name=client_in.email, password=client_in.password
    #     )
    #     send_email(
    #         email_to=client_in.email,
    #         subject=email_data.subject,
    #         html_content=email_data.html_content,
    #     )
    return client
