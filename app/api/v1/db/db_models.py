import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from typing import Optional


class Base(DeclarativeBase):
    pass


class UsersDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(100))

    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer())
    email = mapped_column(
        String(100),
        ForeignKey('users.email')
        )

    title: Mapped[str] = mapped_column(Text())
    description: Mapped[Optional[str]] = mapped_column(String())
    status: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[str] = mapped_column(DateTime(), default=func.now())


class UserTokens(Base):
    __tablename__ = "tokens"

    email = mapped_column(String(100),
                          ForeignKey('users.email'),
                          primary_key=True)
    token = mapped_column(Text())
    expired = mapped_column(DateTime())
