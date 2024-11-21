from sqlmodel import Session, create_engine, select

from .config import settings

from .. import crud
from ..models import Client, ClientCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    client = session.exec(
        select(Client).where(Client.email == settings.FIRST_SUPERUSER)
    ).first()
    if not client:
        client_in = ClientCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        client = crud.create_client(session=session, client_create=client_in)
