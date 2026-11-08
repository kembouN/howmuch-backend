import uuid
from typing import Sequence, Optional
from sqlmodel import Session, select
from app.models.merchant import Merchant
from app.repositories.base_repository import BaseRepository


class MerchantRepository(BaseRepository[Merchant]):
    """Repository pour les opérations CRUD sur Merchant."""

    def __init__(self, session: Session):
        super().__init__(Merchant, session)

    def get_by_location(self, location_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> Sequence[Merchant]:
        """Récupère les commerçants d'une localisation."""
        statement = (
            select(Merchant)
            .where(Merchant.location_id == location_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def search_by_name(self, name: str, *, offset: int = 0, limit: int = 100) -> Sequence[Merchant]:
        """Recherche de commerçants par nom (ILIKE)."""
        statement = select(Merchant).where(Merchant.name.ilike(f"%{name}%")).offset(offset).limit(limit)  # type: ignore
        return self.session.exec(statement).all()
