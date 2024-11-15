import uuid
from typing import Optional

from fastapi import HTTPException, APIRouter

from ..deps import SessionDep
from ... import crud
from ...crud import check_existing_like, check_match_between, update_match_user
from ...models import Client, Like, LikePublic

router = APIRouter()


@router.post("/{liker_id}/like", response_model=LikePublic)
async def like_client(liker_id: uuid.UUID, liked_id: uuid.UUID, session: SessionDep) -> Like:
    """
    Create like
    :param liker_id: UUID of the client who is liking
    :param liked_id: UUID of the client who is being liked
    :param session: Database session
    :return: Created Like object
    """
    if liker_id == liked_id:
        raise HTTPException(
            status_code=400,
            detail="The liker and liked IDs are the same. Self-liking is not allowed."
        )
    db_liker: Client = session.get(Client, liker_id)
    if not db_liker:
        raise HTTPException(
            status_code=400,
            detail="The liker with this ID does not exist in the system."
        )
    db_liked: Client = session.get(Client, liked_id)
    if not db_liked:
        raise HTTPException(
            status_code=400,
            detail="The liked user with this ID does not exist in the system.",
        )
    like: Optional[Like] = await check_existing_like(session=session,
                                                     liker_id=liker_id,
                                                     liked_id=liked_id)

    if like:
        raise HTTPException(status_code=400,
                            detail="This like already exists in the system.")

    like: Like = await crud.create_like(session=session, liker_id=liker_id, liked_id=liked_id)
    match = await check_match_between(liker_id=liker_id, liked_id=liked_id, session=session)
    if match:
        await update_match_user(db_obj=match, session=session)
    return like
