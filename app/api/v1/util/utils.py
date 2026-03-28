import re
from datetime import datetime, timedelta, timezone

import jwt
from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.models import TokenInfo


settings = get_settings()
password_hash = PasswordHash.recommended()


def check_mail(mail: str) -> bool:
    try:
        validate_email(mail)
        return True
    except EmailNotValidError:
        return False


def hash_password(password: str) -> str:
    return password_hash.hash(password=password)


def validate_password(password: str) -> bool:
    pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    return re.match(pattern, password) is not None


def validate_registration_data(email: str, password: str) -> None:
    if check_mail(mail=email):
        if validate_password(password=password):
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Пароль должен содержать минимум 8 символов, заглавную букву, "
                "строчную букву, цифру и специальный символ."
            ),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный email.",
        )


def verify_password(hashed_password: str, password: str) -> bool:
    return password_hash.verify(hash=hashed_password, password=password)


def create_access_token(email: str) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"email": email, "exp": expires_at}
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt, expires_at


def get_jwt(token: str) -> TokenInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        exp = payload.get("exp")
        if exp is None:
            raise credentials_exception

        return TokenInfo(email=email, exp=exp)
    except InvalidTokenError:
        raise credentials_exception
