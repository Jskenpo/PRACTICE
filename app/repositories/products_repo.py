from app.database.engine import get_db_connection

async def count_products():
    """Cuenta el número total de productos en la base de datos."""
    async for connection in get_db_connection():
        result = await connection.execute("SELECT COUNT(*) FROM products")
        total_products = result.scalar()
        return total_products


async def get_products():
    """Obtiene todos los productos de la base de datos."""
    async for connection in get_db_connection():
        result = await connection.execute("SELECT * FROM products")
        products = result.fetchall()
        return products

async def get_product_by_id(product_id: int):
    """Obtiene un producto por su ID."""
    async for connection in get_db_connection():
        result = await connection.execute(
            "SELECT * FROM products WHERE id = :id", {"id": product_id}
        )
        product = result.fetchone()
        return product

async def create_product(name: str, price: float):
    """Crea un nuevo producto en la base de datos."""
    async for connection in get_db_connection():
        await connection.execute(
            "INSERT INTO products (name, price) VALUES (:name, :price)",
            {"name": name, "price": price},
        )
        await connection.commit()