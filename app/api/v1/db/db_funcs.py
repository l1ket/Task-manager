from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Select, Update, Delete

from app.api.v1.db.db_models import Base, UsersDB, UserTokens, Tasks
from app.core.config import get_settings
from app.core.models import TokenInfo, TaskInDB

Settings = get_settings()
USER = Settings.POSTGRES_USER
PASW = Settings.POSTGRES_PASSWORD
PORTS = Settings.PORTS
DB_NAME = Settings.POSTGRES_DB

DATABASE_URL = "postgresql+asyncpg://" + \
    f"{USER}:{PASW}@postgres:{PORTS}/{DB_NAME}"


async def create_engine():
    engine = create_async_engine(
        DATABASE_URL,
        echo=True
    )
    return engine


async def create_session():
    engine = await create_engine()
    session = AsyncSession(engine)
    return session


async def create_tables():
    engine = await create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_user(email: str, passw_hash: str) -> None:
    session = await create_session()
    try:
        user = UsersDB(
            email=email,
            password_hash=passw_hash
            )
        session.add(user)
        await session.commit()
    except Exception as e:
        print('\n\n\n ERROR', e)
    finally:
        await session.close()


async def check_user(email: str):
    session = await create_session()
    try:
        ans = await session.execute(
            Select(UsersDB).where(UsersDB.email == email)
            )
        ans = ans.scalar_one_or_none()
        if ans:
            return True
        else:
            return False
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def check_user_token(email: str):
    session = await create_session()
    try:
        ans = await session.execute(
            Select(UserTokens).where(UserTokens.email == email)
            )
        ans = ans.scalar_one_or_none()
        if ans:
            return True
        else:
            return False
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def update_token(
        info: TokenInfo,
        token: str
        ):
    session = await create_session()
    try:
        ans = await check_user_token(email=info.email)
        if ans:
            ans = await session.execute(
                Update(UserTokens).where(
                    UserTokens.email == info.email
                    ).values(
                    {
                        'token': token,
                        'expired': info.exp
                    }))
            await session.commit()
            return True
        else:
            tokens = UserTokens(
                email=info.email,
                token=token,
                expired=info.exp
            )
            session.add(tokens)
            await session.commit()
            return True
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def get_passw(email: str):
    session = await create_session()
    try:
        ans = await session.execute(
            Select(UsersDB).where(UsersDB.email == email)
            )
        ans = ans.scalar_one_or_none()
        if ans is None:
            return False
        ans_c: UsersDB = ans
        if ans:
            return ans_c.password_hash
        else:
            return False
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def get_tasks(email: str):
    session = await create_session()
    try:
        ans = await session.execute(
            Select(Tasks).where(Tasks.email == email)
            )
        ans = ans.scalars().fetchall()
        return ans
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def create_task_in_db(
    email: str,
    info: TaskInDB
):
    session = await create_session()
    try:
        taks = Tasks(
            email=email,
            title=info.title,
            description=info.description,
            status=info.status,
            task_id=info.task_id
            )
        session.add(taks)
        await session.commit()
        return True
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def get_task(email: str, task_id: int):
    session = await create_session()
    try:
        ans = await session.execute(
            Select(Tasks).where(
                Tasks.email == email,
                Tasks.task_id == task_id)
            )
        ans = ans.scalar_one_or_none()
        return ans
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def update_task(
    email: str,
    task_id: int,
    title: str | None = None,
    status: str | None = None,
    description: str | None = None
        ):
    session = await create_session()

    update_data = {}
    if title is not None:
        update_data["title"] = title
    if status is not None:
        update_data["status"] = status
    if description is not None:
        update_data["description"] = description

    if not update_data:
        return None

    try:
        query = Update(Tasks).where(
                Tasks.email == email,
                Tasks.task_id == task_id).values(
                    **update_data
                )
        await session.execute(query)
        await session.commit()
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()


async def delete_task(
    email: str,
    task_id: int
        ):
    session = await create_session()
    try:
        query = Delete(Tasks).where(
                Tasks.email == email,
                Tasks.task_id == task_id)
        await session.execute(query)
        await session.commit()
    except Exception as e:
        print('\n\n\n ERROR', e)
        return False
    finally:
        await session.close()
