from sqlmodel import Session, create_engine, select

from .. import crud
from .config import settings
from ..models import Client, ClientCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    user = session.exec(
        select(Client).where(Client.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        client_in = ClientCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_client(session=session, client_create=client_in)
