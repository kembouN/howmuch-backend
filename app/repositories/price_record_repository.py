import uuid
from typing import Sequence, Optional
from sqlmodel import Session, select
from app.models.price_record import PriceRecord
from app.repositories.base_repository import BaseRepository


class PriceRecordRepository(BaseRepository[PriceRecord]):
    """Repository pour les opérations CRUD sur PriceRecord."""

    def __init__(self, session: Session):
        super().__init__(PriceRecord, session)

    def get_by_product(self, product_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> Sequence[PriceRecord]:
        """Récupère les enregistrements de prix pour un produit."""
        statement = (
            select(PriceRecord)
            .where(PriceRecord.product_id == product_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_by_user(self, user_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> Sequence[PriceRecord]:
        """Récupère les enregistrements de prix soumis par un utilisateur."""
        statement = (
            select(PriceRecord)
            .where(PriceRecord.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_by_merchant(self, merchant_id: uuid.UUID, *, offset: int = 0, limit: int = 100) -> Sequence[PriceRecord]:
        """Récupère les enregistrements de prix pour un commerçant."""
        statement = (
            select(PriceRecord)
            .where(PriceRecord.merchant_id == merchant_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_latest_for_product(self, product_id: uuid.UUID) -> Optional[PriceRecord]:
        """Récupère le dernier prix enregistré pour un produit."""
        statement = (
            select(PriceRecord)
            .where(PriceRecord.product_id == product_id)
            .order_by(PriceRecord.created_at.desc())  # type: ignore
            .limit(1)
        )
        return self.session.exec(statement).first()
