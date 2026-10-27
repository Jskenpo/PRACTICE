import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, ExpiredSignatureError, jwt
from fastapi import HTTPException, status

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY no está configurada en .env")

ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(minutes=30)


def generate_jwt_token(user_id: str) -> str:
    """Firma un token que identifica al usuario y vence en 30 minutos."""
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + TOKEN_LIFETIME,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    """Valida la firma, el algoritmo y la expiración del token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") is None:
            raise JWTError("Missing expiration")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token vencido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
