from sqlmodel import Session, select
from typing import Optional
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


async def get_client_by_email(*, session: Session, email: str) -> Optional[Client]:
    statement = select(Client).where(Client.email == email)
    session_client = session.exec(statement).first()
    return session_client
