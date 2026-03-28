from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.v1.db.db_models import Base, Tasks, UsersDB
from app.core.config import get_settings
from app.core.models import TaskCreate, TaskUpdate


class UserAlreadyExistsError(Exception):
    pass


settings = get_settings()
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DB_ECHO,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> UsersDB | None:
    result = await session.execute(
        select(UsersDB).where(UsersDB.email == email)
        )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    email: str,
    password_hash: str,
) -> UsersDB:
    user = UsersDB(email=email, password_hash=password_hash)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise UserAlreadyExistsError from exc

    await session.refresh(user)
    return user


async def list_tasks(session: AsyncSession, email: str) -> list[Tasks]:
    result = await session.execute(
        select(Tasks).where(Tasks.email == email).order_by(Tasks.id)
    )
    return list(result.scalars().all())


async def create_task(
    session: AsyncSession,
    email: str,
    payload: TaskCreate,
) -> Tasks:
    task = Tasks(
        email=email,
        title=payload.title,
        description=payload.description,
        status="NEW",
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task_for_user(
    session: AsyncSession,
    email: str,
    task_id: int,
) -> Tasks | None:
    result = await session.execute(
        select(Tasks).where(Tasks.email == email, Tasks.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task(
    session: AsyncSession,
    task: Tasks,
    payload: TaskUpdate,
) -> Tasks:
    update_data = payload.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(task, field_name, value)

    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task: Tasks) -> None:
    await session.delete(task)
    await session.commit()
