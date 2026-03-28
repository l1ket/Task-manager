from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.db import db_funcs as db
from app.api.v1.util.utils import (
    create_access_token,
    hash_password,
    validate_registration_data,
    verify_password,
)
from app.core.models import MessageResponse, RegisterRequest, TokenResponse

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> MessageResponse:
    validate_registration_data(email=payload.email, password=payload.password)

    existing_user = await db.get_user_by_email(
        session=session,
        email=payload.email
        )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует.",
        )

    try:
        await db.create_user(
            session=session,
            email=payload.email,
            password_hash=hash_password(password=payload.password),
        )
    except db.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует.",
        )

    return MessageResponse(message="Пользователь успешно зарегистрирован.")


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(db.get_session)],
) -> TokenResponse:
    user = await db.get_user_by_email(
        session=session,
        email=form_data.username
        )
    if user is None or not verify_password(
        hashed_password=user.password_hash,
        password=form_data.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expires_at = create_access_token(email=user.email)
    return TokenResponse(access_token=access_token, expires_at=expires_at)
