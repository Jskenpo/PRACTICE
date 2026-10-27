from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.repositories.auth_repo import authenticate_user, get_user_by_id
from app.services.auth_services import decode_jwt_token, generate_jwt_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def login(username: str, password: str) -> dict:
    user = authenticate_user(username, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": generate_jwt_token(str(user["id"])),
        "token_type": "bearer",
    }


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_jwt_token(token)
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
