import uuid
from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository for SQLModel entities."""

    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, entity_id: uuid.UUID) -> Optional[ModelType]:
        """Récupère une entité par son ID."""
        return self.session.get(self.model, entity_id)

    def get_all(self, *, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Récupère toutes les entités avec pagination."""
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create(self, entity: ModelType) -> ModelType:
        """Crée une nouvelle entité."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, entity: ModelType, update_data: dict) -> ModelType:
        """Met à jour une entité existante."""
        for key, value in update_data.items():
            if value is not None:
                setattr(entity, key, value)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        """Supprime une entité."""
        self.session.delete(entity)
        self.session.commit()

    def count(self) -> int:
        """Compte le nombre total d'entités."""
        statement = select(self.model)
        return len(self.session.exec(statement).all())
