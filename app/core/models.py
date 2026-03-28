from pydantic import BaseModel, ConfigDict
from datetime import datetime


class User(BaseModel):
    email: str
    created_at: str


class UserInDB(User):
    password_hash: str


class TokenInfo(BaseModel):
    email: str
    exp: datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskInDB(TaskCreate):
    task_id: int
    status: str


class FullUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    password_hash: str
    created_at: datetime


class FullTasks(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    email: str
    title: str
    description: str
    status: str
    created_at: datetime
