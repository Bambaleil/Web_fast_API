from typing import Generator, Annotated, Type

import jwt
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from ..core import security
from ..core.config import settings
from ..core.db import engine
from ..models import Client, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_client(session: SessionDep, token: TokenDep) -> Type[Client]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    client = session.get(Client, token_data.sub)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not client.is_active:
        raise HTTPException(status_code=400, detail="Inactive client")
    return client


CurrentClient = Annotated[Client, Depends(get_current_client)]


def get_current_active_superuser(current_client: CurrentClient) -> Client:
    if not current_client.is_superuser:
        raise HTTPException(
            status_code=403, detail="The client doesn't have enough privileges"
        )
    return current_client
