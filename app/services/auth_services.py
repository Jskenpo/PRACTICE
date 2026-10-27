from jose import jwt
from fastapi import HTTPException, status


def generate_jwt_token(payload: dict, secret_key: str, algorithm: str = "HS256") -> str:
    """
    Generate a JWT token.

    Args:
        payload (dict): The payload to encode in the JWT.
        secret_key (str): The secret key used to sign the JWT.
        algorithm (str): The algorithm used for signing the JWT. Default is "HS256".

    Returns:
        str: The generated JWT token.
    """
    return jwt.encode(payload, secret_key, algorithm=algorithm)

def decode_jwt_token(token: str, secret_key: str, algorithms: list = ["HS256"]) -> dict:
    """
    Decode a JWT token.

    Args:
        token (str): The JWT token to decode.
        secret_key (str): The secret key used to verify the JWT.
        algorithms (list): A list of algorithms to use for decoding. Default is ["HS256"].

    Returns:
        dict: The decoded payload from the JWT.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )