from enum import Enum
import uuid as uuid_pkg
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.user_account import UserAccount
    from app.models.price_record import PriceRecord


class ProductSource(str, Enum):
    CROWDSOURCED = "crowdsourced"
    SCRAPED = "scraped"
    WFP = "wfp"

class Product(BaseModel, table=True):
    """Produit référencé dans l'application."""
    __tablename__ = "products"

    name: str = Field(nullable=False, index=True)
    category: Optional[str] = Field(default=None, index=True)
    source: Optional[ProductSource] = Field(default=None)
    generic_name: Optional[str] = Field(default=None)
    unit: Optional[str] = Field(default=None)

    # --- foreign keys ---
    user_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="user_account.id", index=True
    )

    # --- relationships ---
    user: Optional["UserAccount"] = Relationship(back_populates="products")
    price_records: list["PriceRecord"] = Relationship(back_populates="product")
