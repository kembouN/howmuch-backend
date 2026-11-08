from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field
from app.models.base_model import BaseModel


class ImportSource(str, Enum):
    WFP_CSV = "wfp_csv"
    WEB_SCRAPING = "web_scraping"
    CROWDSOURCING = "crowdsourcing"


class ImportStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DataImport(BaseModel, table=True):
    """Journal d'audit et suivi des imports de données (ETL WFP CSV & Web Scraping)."""
    __tablename__ = "data_imports"

    source: str = Field(default=ImportSource.WFP_CSV.value, index=True, nullable=False)
    target: Optional[str] = Field(default=None, description="Nom de fichier CSV ou URL/cible du scraping")
    status: str = Field(default=ImportStatus.PENDING.value, index=True, nullable=False)
    records_imported: int = Field(default=0)
    records_skipped: int = Field(default=0)
    error_log: Optional[str] = Field(default=None)
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    finished_at: Optional[datetime] = Field(default=None)
