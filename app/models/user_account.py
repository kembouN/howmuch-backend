from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.price_record import PriceRecord


class UserRole(str, Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"


class UserAccount(BaseModel, table=True):
    """Compte utilisateur."""
    __tablename__ = "user_account"

    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: str = Field(default=UserRole.CITIZEN.value, nullable=False)
    is_active: bool = Field(default=True)
    is_blocked: bool = Field(default=False)
    report_count: int = Field(default=0)

    # --- relationships ---
    products: list["Product"] = Relationship(back_populates="user")
    price_records: list["PriceRecord"] = Relationship(back_populates="user")
