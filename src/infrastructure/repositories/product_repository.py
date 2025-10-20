"""
Repositorio concreto de productos usando SQLAlchemy.
Cumple el contrato IProductRepository del dominio.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel

def _model_to_entity(m: ProductModel) -> Product:
    return Product(id=m.id, name=m.name, brand=m.brand, category=m.category,
                   size=m.size, color=m.color, price=m.price, stock=m.stock,
                   description=m.description or "")

def _entity_to_model(e: Product) -> ProductModel:
    return ProductModel(id=e.id, name=e.name, brand=e.brand, category=e.category,
                        size=e.size, color=e.color, price=e.price, stock=e.stock,
                        description=e.description or "")

class SQLProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Product]:
        rows = self.db.query(ProductModel).all()
        return [_model_to_entity(r) for r in rows]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        r = self.db.get(ProductModel, product_id)
        return _model_to_entity(r) if r else None

    def get_by_brand(self, brand: str) -> List[Product]:
        rows = self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        return [_model_to_entity(r) for r in rows]

    def get_by_category(self, category: str) -> List[Product]:
        rows = self.db.query(ProductModel).filter(ProductModel.category == category).all()
        return [_model_to_entity(r) for r in rows]

    def save(self, product: Product) -> Product:
        if product.id is None:
            orm = _entity_to_model(product)
            self.db.add(orm)
            self.db.commit()
            self.db.refresh(orm)
            return _model_to_entity(orm)
        existing = self.db.get(ProductModel, product.id)
        if not existing:
            orm = _entity_to_model(product)
            self.db.add(orm); self.db.commit(); self.db.refresh(orm)
            return _model_to_entity(orm)
        for f in ("name","brand","category","size","color","price","stock","description"):
            setattr(existing, f, getattr(product, f))
        self.db.commit(); self.db.refresh(existing)
        return _model_to_entity(existing)

    def delete(self, product_id: int) -> bool:
        obj = self.db.get(ProductModel, product_id)
        if not obj:
            return False
        self.db.delete(obj); self.db.commit()
        return True