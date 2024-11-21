import uuid
from typing import Optional, Sequence

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ... import crud
from ...models import Client, Like, LikePublic
from ...utils import generate_match_email, send_email
from ..deps import SessionDep

router = APIRouter()


@router.post("/{liker_id}/like", response_model=LikePublic)
async def like_client(
    liker_id: uuid.UUID,
    liked_id: uuid.UUID,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Like:
    """
    Создание лайка и проверка на совпадение.

    Эндпоинт позволяет участнику с идентификатором `liker_id`
    поставить лайк участнику с идентификатором `liked_id`.
    Если лайк уже существует, возвращается ошибка.
    После успешного создания лайка проверяется,
    есть ли взаимный лайк (match), и если он найден,
    обновляется статус обоих лайков.

    Параметры:
    - **background_tasks**: Фоновые задачи.
    - **liker_id**: UUID участника, ставящего лайк.
    - **liked_id**: UUID участника, получающего лайк.
    - **session**: Сессия базы данных.

    Возвращает:
    - Созданный объект Like.

    Исключения:
    - **HTTPException 400**: Если лайк уже существует.
    - **HTTPException 400**: Если участник, ставящий лайк, не существует.
    - **HTTPException 400**: Если участник, получающий лайк, не существует.
    - **HTTPException 400**: Если идентификаторы лайкающего и
     получающего лайк совпадают.
    """

    if liker_id == liked_id:
        raise HTTPException(
            status_code=400,
            detail="The liker and liked IDs are the same."
            " Self-liking is not allowed.",
        )
    db_liker: Client = session.get(Client, liker_id)
    if not db_liker:
        raise HTTPException(
            status_code=400,
            detail="The liker with this ID does not exist in the system.",
        )
    db_liked: Client = session.get(Client, liked_id)
    if not db_liked:
        raise HTTPException(
            status_code=400,
            detail="The liked user with this ID does not exist in the system.",
        )
    like: Optional[Like] = await crud.check_existing_like(
        session=session, liker_id=liker_id, liked_id=liked_id
    )

    if like:
        raise HTTPException(
            status_code=400, detail="This like already exists in the system."
        )

    like: Like = await crud.create_like(
        session=session, liker_id=liker_id, liked_id=liked_id
    )
    list_liked: Sequence[Optional[Like]] = await crud.find_like_client(
        session=session, liked_id=liked_id
    )
    if list_liked:
        match: Optional[Like] = await crud.check_match_between(
            liker_id=liker_id, list_liked=list_liked
        )
        if match:
            await crud.update_match_user(
                liker_obj=like, liked_obj=match, session=session
            )
            (email_data_1, email_data_2) = await generate_match_email(
                liker_obj=db_liker, liked_obj=db_liked
            )
            background_tasks.add_task(
                send_email,
                email_to=db_liker.email,
                subject=email_data_1.subject,
                html_content=email_data_1.html_content,
            )
            background_tasks.add_task(
                send_email,
                email_to=db_liked.email,
                subject=email_data_2.subject,
                html_content=email_data_2.html_content,
            )
    return like
