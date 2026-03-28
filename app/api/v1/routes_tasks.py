from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated

from app.api.v1.db.db_funcs import get_tasks, create_task_in_db, \
    get_task, update_task, delete_task
from app.api.v1.util.utils import get_jwt
from app.core.models import TaskInDB, TaskCreate, FullTasks

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


async def check_user(
    token: Annotated[str, Depends(oauth2_scheme)]
        ):
    token_info = await get_jwt(token=token)
    return token_info.email


async def common_parameters(
    task_id: int | None = None,
    title: str | None = None,
    status: str | None = None,
    description: str | None = None
        ):
    return {
        'task_id': task_id,
        'title': title,
        'status': status,
        'description': description
        }


@router.get('/tasks')
async def get_tasks_from_db(
    email: Annotated[str, Depends(check_user)],
    commons: Annotated[dict, Depends(common_parameters)]
        ):
    tasks = await get_tasks(email=email)
    return tasks


@router.get('/tasks/{task_id}')
async def get_task_from_db(
    email: Annotated[str, Depends(check_user)],
    commons: Annotated[dict, Depends(common_parameters)]
        ):
    if commons['task_id']:
        task = await get_task(
            email=email,
            task_id=commons['task_id']
            )
        task = FullTasks.model_validate(task).model_dump()
        return task
    else:
        raise HTTPException(
            status_code=400,
            detail='Нужен id taks-а для вывода'
        )


@router.post('/tasks/create')
async def create_task(
    email: Annotated[str, Depends(check_user)],
    info: TaskCreate
        ) -> bool:
    tasks_len = len(await get_tasks(email=email))
    if tasks_len > 0:
        info_add = TaskInDB(
            status='NEW',
            title=info.title,
            description=info.description,
            task_id=tasks_len+1
            )
        return await create_task_in_db(
            email=email, info=info_add
        )
    else:
        info_add = TaskInDB(
            status='NEW',
            title=info.title,
            description=info.description,
            task_id=1
            )
        return await create_task_in_db(
            email=email, info=info_add
        )


@router.put('/tasks/')
async def change_task(
    email: Annotated[str, Depends(check_user)],
    commons: Annotated[dict, Depends(common_parameters)]
        ):
    if commons['task_id']:
        await update_task(
            email=email,
            **commons
            )
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail='Нужен id taks-а для изменения'
        )


@router.delete('/tasks/')
async def delete(
    email: Annotated[str, Depends(check_user)],
    commons: Annotated[dict, Depends(common_parameters)]
        ):
    if commons['task_id']:
        await delete_task(
            email=email,
            task_id=commons['task_id']
            )
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail='Нужен id taks-а для изменения'
        )
