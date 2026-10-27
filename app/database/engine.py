import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine


load_dotenv()

password = os.getenv("POSTGRES_PASSWORD")
if not password:
    raise RuntimeError(
        "POSTGRES_PASSWORD no está configurada. Define la variable en el archivo .env."
    )

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username="practice",
    password=password,
    host="127.0.0.1",
    port=5433,
    database="practice",
)

engine: Engine = create_engine(database_url)

async def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    with engine.connect() as connection:
        yield connection