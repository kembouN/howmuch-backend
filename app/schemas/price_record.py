import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


# --- Create / Update ---

class PriceRecordCreate(SQLModel):
    """Schéma pour la création d'un enregistrement de prix."""
    product_price: float
    source_type: Optional[str] = None
    price_day: Optional[str] = None
    status: Optional[str] = None
    in_stock: bool = True
    product_id: uuid.UUID
    merchant_id: Optional[uuid.UUID] = None


class PriceRecordUpdate(SQLModel):
    """Schéma pour la mise à jour d'un enregistrement de prix."""
    product_price: Optional[float] = None
    source_type: Optional[str] = None
    price_day: Optional[str] = None
    status: Optional[str] = None
    in_stock: Optional[bool] = None


# --- Read ---

class PriceRecordRead(SQLModel):
    """Schéma de lecture d'un enregistrement de prix."""
    id: uuid.UUID
    product_price: float
    source_type: Optional[str]
    price_day: Optional[str]
    status: Optional[str]
    in_stock: bool
    product_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    merchant_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
