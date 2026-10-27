from fastapi import HTTPException
from app.repositories.products_repo import get_products as repo_get_products
from app.repositories.products_repo import get_product_by_id as repo_get_product_by_id
from app.repositories.products_repo import create_product as repo_create_product
from app.repositories.products_repo import count_products as repo_count_products



async def count_products():
    """Obtiene el número total de productos en la base de datos."""
    total_products = repo_count_products()
    return {"total_products": total_products}


async def create_product(name: str, price: float):
    """Crea un nuevo producto en la base de datos."""
    await repo_create_product(name, price)


async def get_product_by_id(product_id: int):
    """Obtiene un producto por su ID."""
    product = await repo_get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

async def get_products():
    """Obtiene todos los productos de la base de datos."""
    products = await repo_get_products()
    return products
