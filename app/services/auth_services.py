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