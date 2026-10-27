from sqlalchemy import text

from app.database.engine import get_db_connection


def count_products():
    """Cuenta el número total de productos en la base de datos."""
    with get_db_connection() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM products"))
        total_products = result.scalar()
        return total_products


def get_products():
    """Obtiene todos los productos de la base de datos."""
    with get_db_connection() as connection:
        result = connection.execute(text("SELECT id,name,price_cents,stock FROM products"))
        products = result.fetchall()
        dict_products = [dict(row) for row in products]  # Convertir Row a diccionario
        return dict_products


def get_product_by_id(product_id: int):
    """Obtiene un producto por su ID."""
    with get_db_connection() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE id = :id"), {"id": product_id}
        )
        product = result.fetchone()
        dict_product = dict(product) if product else None  # Convertir Row a diccionario
        return dict_product


def create_product(name: str, price: float):
    """Crea un nuevo producto en la base de datos."""
    with get_db_connection() as connection:
        connection.execute(
            text("INSERT INTO products (name, price_cents) VALUES (:name, :price)"),
            {"name": name, "price": price},
        )
        connection.commit()