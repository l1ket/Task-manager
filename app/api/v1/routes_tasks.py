from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.db import db_funcs as db
from app.api.v1.db.db_models import Tasks
from app.api.v1.util.utils import get_jwt
from app.core.models import MessageResponse, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(tags=["tasks"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user_email(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    token_info = get_jwt(token=token)
    return str(token_info.email)


async def get_owned_task(
    task_id: int,
    email: Annotated[str, Depends(get_current_user_email)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> Tasks:
    task = await db.get_task_for_user(session=session, email=email, task_id=task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена.",
        )
    return task


@router.get("/tasks", response_model=list[TaskRead])
async def get_tasks_from_db(
    email: Annotated[str, Depends(get_current_user_email)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> list[TaskRead]:
    return await db.list_tasks(session=session, email=email)


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task_from_db(
    task: Annotated[Tasks, Depends(get_owned_task)],
) -> TaskRead:
    return task


@router.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    payload: TaskCreate,
    email: Annotated[str, Depends(get_current_user_email)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> TaskRead:
    return await db.create_task(session=session, email=email, payload=payload)


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def change_task(
    payload: TaskUpdate,
    task: Annotated[Tasks, Depends(get_owned_task)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> TaskRead:
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно передать хотя бы одно поле для обновления.",
        )

    return await db.update_task(session=session, task=task, payload=payload)


@router.delete("/tasks/{task_id}", response_model=MessageResponse)
async def delete_task(
    task: Annotated[Tasks, Depends(get_owned_task)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> MessageResponse:
    await db.delete_task(session=session, task=task)
    return MessageResponse(message="Задача удалена.")
