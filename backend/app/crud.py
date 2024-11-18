import uuid
from typing import Optional, Sequence

from sqlmodel import Session, select

from .core.security import get_password_hash
from .models import ClientCreate, Client, Like, FilterClient


async def get_list_filter_client(*, session: Session, filter_client: FilterClient):
    statement = select(Client)
    if filter_client.sex:
        statement = statement.where(Client.sex == filter_client.sex)
    if filter_client.name:
        statement = statement.where(Client.name.ilike(f"%{filter_client.name}%"))
    if filter_client.surname:
        statement = statement.where(Client.surname.ilike(f"%{filter_client.surname}%"))
    clients: Sequence[Optional[Client]] = session.exec(statement).all()
    return clients


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
    session_client: Optional[Client] = session.exec(statement).first()
    return session_client


async def check_existing_like(*, session: Session, liker_id: uuid.UUID, liked_id: uuid.UUID) -> Optional[Like]:
    statement = select(Like).where((Like.liker_id == liker_id) & (Like.liked_id == liked_id))
    existing_like: Optional[Like] = session.exec(statement).first()
    return existing_like


async def create_like(*, session: Session, liker_id: uuid.UUID, liked_id: uuid.UUID) -> Like:
    db_obj = Like(
        liker_id=liker_id,
        liked_id=liked_id
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


async def find_like_client(*, session: Session, liked_id: uuid.UUID) -> Sequence[Optional[Like]]:
    statement = select(Like).where(Like.liker_id == liked_id, Like.match == False)
    db_obj: Sequence[Optional[Like]] = session.exec(statement).all()
    return db_obj


async def check_match_between(*, liker_id: uuid.UUID, list_liked: Sequence[Like]) -> Optional[Like]:
    for info in list_liked:
        if info.liked_id == liker_id:
            return info
    return None


async def update_match_user(*, session: Session, liked_obj: Like, liker_obj: Like) -> None:
    liker_obj.match = True
    liked_obj.match = True
    session.bulk_save_objects([liker_obj, liked_obj])
    session.commit()
