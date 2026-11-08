import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


# --- Create / Update ---

class MerchantCreate(SQLModel):
    """Schéma pour la création d'un commerçant."""
    name: str
    type: Optional[str] = None
    is_guard: bool = False
    location_id: Optional[uuid.UUID] = None


class MerchantUpdate(SQLModel):
    """Schéma pour la mise à jour d'un commerçant."""
    name: Optional[str] = None
    type: Optional[str] = None
    is_guard: Optional[bool] = None
    location_id: Optional[uuid.UUID] = None


# --- Read ---

class MerchantRead(SQLModel):
    """Schéma de lecture d'un commerçant."""
    id: uuid.UUID
    name: str
    type: Optional[str]
    is_guard: bool
    location_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
