from typing import Sequence, Optional
from sqlmodel import Session, select
from app.models.location import Location
from app.repositories.base_repository import BaseRepository


class LocationRepository(BaseRepository[Location]):
    """Repository pour les opérations CRUD sur Location."""

    def __init__(self, session: Session):
        super().__init__(Location, session)

    def get_by_city(self, city: str, *, offset: int = 0, limit: int = 100) -> Sequence[Location]:
        """Récupère les localisations d'une ville."""
        statement = select(Location).where(Location.city == city).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def search_by_neighborhood(self, neighborhood: str, *, offset: int = 0, limit: int = 100) -> Sequence[Location]:
        """Recherche par quartier (ILIKE)."""
        statement = (
            select(Location)
            .where(Location.neighborhood.ilike(f"%{neighborhood}%"))  # type: ignore
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()
