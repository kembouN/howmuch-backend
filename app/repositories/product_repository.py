import uuid
from typing import Sequence, Optional
from sqlmodel import Session, select
from app.models.product import Product
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository pour les opérations CRUD sur Product."""

    def __init__(self, session: Session):
        super().__init__(Product, session)

    def get_by_category(self, category: str, *, offset: int = 0, limit: int = 100) -> Sequence[Product]:
        """Récupère les produits par catégorie."""
        statement = select(Product).where(Product.category == category).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_by_user(self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> Sequence[Product]:
        """Récupère les produits soumis par un utilisateur."""
        statement = select(Product).where(Product.user_id == user_id).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def search_by_name(self, name: str, *, offset: int = 0, limit: int = 100) -> Sequence[Product]:
        """Recherche de produits par nom (ILIKE)."""
        statement = select(Product).where(Product.name.ilike(f"%{name}%")).offset(offset).limit(limit)  # type: ignore
        return self.session.exec(statement).all()
