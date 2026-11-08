import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


# --- Create / Update ---

class LocationCreate(SQLModel):
    """Schéma pour la création d'une localisation."""
    city: str
    neighborhood: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class LocationUpdate(SQLModel):
    """Schéma pour la mise à jour d'une localisation."""
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


# --- Read ---

class LocationRead(SQLModel):
    """Schéma de lecture d'une localisation."""
    id: uuid.UUID
    city: str
    neighborhood: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    created_at: datetime
    updated_at: datetime
