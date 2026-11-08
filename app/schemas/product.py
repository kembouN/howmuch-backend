import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


# --- Create / Update ---

class ProductCreate(SQLModel):
    """Schéma pour la création d'un produit."""
    name: str
    category: Optional[str] = None
    source: Optional[str] = None
    generic_name: Optional[str] = None
    unit: Optional[str] = None


class ProductUpdate(SQLModel):
    """Schéma pour la mise à jour d'un produit."""
    name: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    generic_name: Optional[str] = None
    unit: Optional[str] = None


# --- Read ---

class ProductRead(SQLModel):
    """Schéma de lecture d'un produit."""
    id: uuid.UUID
    name: str
    category: Optional[str]
    source: Optional[str]
    generic_name: Optional[str]
    unit: Optional[str]
    user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
