from uuid import UUID

from sqlalchemy import text

from app.database.engine import get_db_connection


def authenticate_user(username: str, password: str) -> dict | None:
    """Busca un usuario y verifica su contraseña con el hash bcrypt guardado."""
    with get_db_connection() as connection:
        row = connection.execute(
            text("""
                SELECT id, username, role
                FROM users
                WHERE username = :username
                  AND password_hash = crypt(:password, password_hash)
            """),
            {"username": username, "password": password},
        ).mappings().first()
        return dict(row) if row is not None else None


def get_user_by_id(user_id: UUID) -> dict | None:
    with get_db_connection() as connection:
        row = connection.execute(
            text("SELECT id, username, role FROM users WHERE id = :id"),
            {"id": user_id},
        ).mappings().first()
        return dict(row) if row is not None else None
