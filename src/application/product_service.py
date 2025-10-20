"""
Servicio de aplicación para gestionar productos.
Orquesta casos de uso sobre IProductRepository.
"""

from typing import Any, Dict, List, Optional

from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.domain.repositories import IProductRepository
from .dtos import ProductDTO


class ProductService:
    """
    Casos de uso de productos (Application Layer).

    Constructor:
        repo: IProductRepository (inyectado)
    Métodos:
        - get_all_products()
        - get_product_by_id(product_id)
        - search_products(filters)
        - create_product(product_dto)
        - update_product(product_id, product_dto)
        - delete_product(product_id)
        - get_available_products()
    """

    def __init__(self, repo: IProductRepository):
        self._repo = repo

    def get_all_products(self) -> List[Product]:
        return self._repo.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        prod = self._repo.get_by_id(product_id)
        if prod is None:
            raise ProductNotFoundError(product_id)
        return prod

    def search_products(self, filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        """
        Filtra por criterios. Soporta:
          - brand
          - category
        Otros criterios (size, color, min_price, max_price) se pueden
        filtrar en memoria si llegan en `filters`.
        """
        filters = filters or {}
        brand = filters.get("brand")
        category = filters.get("category")

        # Usa los métodos del repositorio cuando existan
        if brand and category:
            # Intersección simple
            by_brand = {p.id: p for p in self._repo.get_by_brand(brand)}
            result = [p for p in self._repo.get_by_category(category) if p.id in by_brand]
        elif brand:
            result = self._repo.get_by_brand(brand)
        elif category:
            result = self._repo.get_by_category(category)
        else:
            result = self._repo.get_all()

        # Filtros opcionales en memoria
        size = filters.get("size")
        color = filters.get("color")
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")

        def ok(p: Product) -> bool:
            if size and p.size != size:
                return False
            if color and p.color != color:
                return False
            if min_price is not None and p.price < float(min_price):
                return False
            if max_price is not None and p.price > float(max_price):
                return False
            return True

        return [p for p in result if ok(p)]

    def create_product(self, product_dto: ProductDTO) -> Product:
        """
        Crea un Product desde ProductDTO y lo guarda.
        Lanza InvalidProductDataError si el dominio rechaza los datos.
        """
        try:
            prod = Product(
                id=None,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e)) from e

        return self._repo.save(prod)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """
        Actualiza un producto existente. Valida existencia previa.
        """
        existing = self._repo.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id)

        try:
            updated = Product(
                id=product_id,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e)) from e

        return self._repo.save(updated)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto. Lanza ProductNotFoundError si no existe.
        """
        existed = self._repo.delete(product_id)
        if not existed:
            raise ProductNotFoundError(product_id)
        return True

    def get_available_products(self) -> List[Product]:
        """Retorna solo productos con stock > 0."""
        return [p for p in self._repo.get_all() if p.is_available()]