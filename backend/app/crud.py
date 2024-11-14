from sqlmodel import Session

from .core.security import get_password_hash
from .models import ClientCreate, Client


async def create_client(*, session: Session, client_create: ClientCreate) -> Client:
    db_obj = Client.model_validate(
        client_create, update={"hashed_password": await get_password_hash(client_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
