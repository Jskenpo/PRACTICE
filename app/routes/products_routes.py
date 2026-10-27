from fastapi   import APIRouter, HTTPException, Depends
from app.controllers.products_controller import get_products, get_product_by_id, create_product, count_products
from uuid import UUID

router = APIRouter()

@router.get("/")
def read_products():
    """Obtiene todos los productos."""
    return get_products()

@router.get("/count")
def count_all_products():
    """Cuenta el número total de productos."""
    return count_products()

'''Espera un uuid de producto como parámetro y devuelve el producto correspondiente. Si no se encuentra el producto, lanza una excepción HTTP 404.'''
@router.get("/{product_id}")
def read_product(product_id: UUID):
    """Obtiene un producto por su ID."""
    return get_product_by_id(product_id)

@router.post("/")
def add_product(name: str, price: float):
    """Crea un nuevo producto."""
    create_product(name, price)
    return {"message": "Producto creado exitosamente"}




