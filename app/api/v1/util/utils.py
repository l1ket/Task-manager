import re
import jwt

from email_validator import validate_email, EmailNotValidError
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings
from app.core.models import TokenInfo


Settings = get_settings()
SECRET_KEY = Settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440    # 24 hours


def check_mail(mail: str) -> bool:
    try:
        validate_email(mail)
        return True
    except EmailNotValidError:
        return False


async def hash_passw(paswrd: str) -> str:
    password_hash = PasswordHash.recommended()
    hash_pass = password_hash.hash(password=paswrd)
    return hash_pass


def validate_password(paswrd: str) -> bool:
    pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    return re.match(pattern, paswrd) is not None


async def base_check(email: str, passw: str):
    if check_mail(mail=email):
        if validate_password(paswrd=passw):
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пароль должен соответствовать стандартным правилам'
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Некорректный email'
            )


async def verify_pass(hasded_p: str, passw: str):
    password_hash = PasswordHash.recommended()
    return password_hash.verify(hash=hasded_p, password=passw)


async def create_jwt(username: str) -> tuple[str, dict]:
    expire = datetime.now() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    encode = {'email': username, 'exp': expire}
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, encode


async def get_jwt(token: str) -> TokenInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('email')
        if email is None:
            raise credentials_exception
        exp = payload.get('exp')
        if exp is None:
            raise credentials_exception

        token_info = TokenInfo(email=email, exp=exp)
        return token_info
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
