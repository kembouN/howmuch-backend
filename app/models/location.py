import uuid as uuid_pkg
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.merchant import Merchant


class Location(BaseModel, table=True):
    """Localisation géographique (ville / quartier)."""
    __tablename__ = "locations"

    city: str = Field(nullable=False, index=True)
    neighborhood: Optional[str] = Field(default=None)
    latitude: Optional[str] = Field(default=None)
    longitude: Optional[str] = Field(default=None)

    # --- relationships ---
    merchants: list["Merchant"] = Relationship(back_populates="location")
