import uuid as uuid_pkg
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.price_record import PriceRecord


class Merchant(BaseModel, table=True):
    """Commerçant / point de vente."""
    __tablename__ = "merchants"

    name: str = Field(nullable=False, index=True)
    type: Optional[str] = Field(default=None)
    is_guard: bool = Field(default=False)

    # --- foreign keys ---
    location_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="locations.id", index=True
    )

    # --- relationships ---
    location: Optional["Location"] = Relationship(back_populates="merchants")
    price_records: list["PriceRecord"] = Relationship(back_populates="merchant")
