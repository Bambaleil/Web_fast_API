import uuid

from sqlmodel import Session, select
from typing import Optional
from .core.security import get_password_hash
from .models import ClientCreate, Client, Like


async def create_client(*, session: Session, client_create: ClientCreate) -> Client:
    db_obj = Client.model_validate(
        client_create, update={"hashed_password": await get_password_hash(client_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


async def get_client_by_email(*, session: Session, email: str) -> Optional[Client]:
    statement: select = select(Client).where(Client.email == email)
    session_client: Optional[Client] = session.exec(statement).first()
    return session_client


async def check_existing_like(*, session: Session, liker_id: uuid.UUID, liked_id: uuid.UUID) -> Optional[Like]:
    statement = select(Like).where((Like.liker_id == liker_id) & (Like.liked_id == liked_id))
    existing_like: Optional[Like] = session.exec(statement).first()
    return existing_like

