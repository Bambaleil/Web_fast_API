from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import SessionDep, CurrentClient
from app.core import security
from app.core.config import settings
from app.models import Token, ClientPublic

router = APIRouter()


@router.post("/login/access-token")
async def login_access_token(
        session: SessionDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    client = await crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not client:
        raise HTTPException(status_code=400,
                            detail="Incorrect email or password")
    elif not client.is_active:
        raise HTTPException(status_code=400,
                            detail="Inactive user")
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            client.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=ClientPublic)
def test_token(current_client: CurrentClient) -> Any:
    """
    Test access token
    """
    return current_client
