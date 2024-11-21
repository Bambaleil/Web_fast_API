import uuid
from typing import Optional, Sequence, List

from aiocache import cached
from sqlmodel import Session, select

from .core.security import get_password_hash, verify_password
from .models import ClientCreate, Client, Like, FilterClient, ClientUpdateLocation
from .utils import great_circle_distance


@cached(ttl=600)
async def get_clients_within_distance(*, session: Session, current_lat: float, current_lon: float, distance: float,
                                      current_email: str) -> List[Client]:
    statement = select(Client).where(Client.latitude.isnot(None), Client.longitude.isnot(None),
                                     Client.email != current_email)
    clients_within_distance: List[Client.id] = [
        client.id for client in session.exec(statement).all() if distance >= great_circle_distance(
            lat1=current_lat, lon1=current_lon, lat2=client.latitude, lon2=client.longitude
        )]
    return clients_within_distance


async def get_list_filter_client(*, session: Session, filter_client: FilterClient, current_client):
    statement = select(Client)
    if filter_client.sex:
        statement = statement.where(Client.sex == filter_client.sex)
    if filter_client.name:
        statement = statement.where(Client.name.ilike(f"%{filter_client.name}%"))
    if filter_client.surname:
        statement = statement.where(Client.surname.ilike(f"%{filter_client.surname}%"))
    if filter_client.distance:
        clients_within_distance_ids = await get_clients_within_distance(session=session,
                                                                        current_lat=current_client.latitude,
                                                                        current_lon=current_client.longitude,
                                                                        distance=filter_client.distance,
                                                                        current_email=current_client.email)
        statement = statement.where(Client.id.in_(clients_within_distance_ids))
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


async def update_client(*, session: Session, db_client: Client, client_up: ClientUpdateLocation) -> Client:
    client_data = client_up.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in client_data:
        password = client_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_client.sqlmodel_update(client_data, update=extra_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


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


async def authenticate(*, session: Session, email: str, password: str) -> Optional[Client]:
    db_client: Optional[Client] = await get_client_by_email(session=session, email=email)
    if not db_client:
        return None
    if not verify_password(password, db_client.hashed_password):
        return None
    return db_client
