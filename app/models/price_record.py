import uuid as uuid_pkg
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user_account import UserAccount
    from app.models.merchant import Merchant


class PriceRecord(BaseModel, table=True):
    """Enregistrement de prix soumis par un utilisateur."""
    __tablename__ = "price_records"

    product_price: float = Field(nullable=False)
    source_type: Optional[str] = Field(default=None)
    price_day: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    in_stock: bool = Field(default=True)

    # --- foreign keys ---
    product_id: uuid_pkg.UUID = Field(
        foreign_key="products.id", nullable=False, index=True
    )
    user_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="user_account.id", index=True
    )
    merchant_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="merchants.id", index=True
    )

    # --- relationships ---
    product: Optional["Product"] = Relationship(back_populates="price_records")
    user: Optional["UserAccount"] = Relationship(back_populates="price_records")
    merchant: Optional["Merchant"] = Relationship(back_populates="price_records")
