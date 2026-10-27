from fastapi   import APIRouter, HTTPException, Depends
from app.controllers.products_controller import get_products, get_product_by_id, create_product, count_products
from uuid import UUID

router = APIRouter()

@router.get("/")
async def read_products():
    """Obtiene todos los productos."""
    return await get_products()

@router.get("/count")
async def count_all_products():
    """Cuenta el número total de productos."""
    return await count_products()

'''Espera un uuid de producto como parámetro y devuelve el producto correspondiente. Si no se encuentra el producto, lanza una excepción HTTP 404.'''
@router.get("/{product_id}")
async def read_product(product_id: UUID):
    """Obtiene un producto por su ID."""
    return await get_product_by_id(product_id)

@router.post("/")
async def add_product(name: str, price: float):
    """Crea un nuevo producto."""
    await create_product(name, price)
    return {"message": "Producto creado exitosamente"}




