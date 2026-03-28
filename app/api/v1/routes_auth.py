from typing import Annotated

from app.api.v1.util.utils import hash_passw, base_check, create_jwt, \
    verify_pass
from app.api.v1.db.db_funcs import check_user, create_user, update_token, \
    get_passw
from app.core.models import TokenInfo

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


class RegParametrs:
    def __init__(self, email: str, passw: str):
        self.email = email
        self.passw = passw


class Details:
    def __init__(self):
        self.reg = 'email уже существует'
        self.login = 'Неверное имя пользователя или пароль'


@router.post('/auth/register')
async def register(reg_params: RegParametrs = Depends(RegParametrs)):
    email, passw = reg_params.email, reg_params.passw
    if await base_check(email=email, passw=passw):
        if not await check_user(email=email):
            passw_h = await hash_passw(paswrd=passw)
            await create_user(email=email, passw_hash=passw_h)
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=Details().reg
            )


@router.post('/auth/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email, passw = form_data.username, form_data.password
    if await base_check(email=email, passw=passw):
        if not await check_user(email=email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=Details().login
            )
        hashed_p = await get_passw(email=email)
        if isinstance(hashed_p, str):
            if await verify_pass(hasded_p=hashed_p, passw=passw):
                token, info = await create_jwt(username=email)
                info = TokenInfo(**info)
                if await update_token(
                        info=info,
                        token=token
                        ):
                    return {
                        "access_token": token,
                        "token_type": "bearer"
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Details().login
                )
        else:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
