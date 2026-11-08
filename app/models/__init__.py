# Import all models so SQLModel registers their metadata
from app.models.base_model import BaseModel
from app.models.user_account import UserAccount, UserRole
from app.models.product import Product
from app.models.price_record import PriceRecord
from app.models.merchant import Merchant
from app.models.location import Location
from app.models.data_import import DataImport, ImportSource, ImportStatus

__all__ = [
    "BaseModel",
    "UserAccount",
    "UserRole",
    "Product",
    "PriceRecord",
    "Merchant",
    "Location",
    "DataImport",
    "ImportSource",
    "ImportStatus",
]
