import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


# --- Create / Update ---

class DataImportCreate(SQLModel):
    """Schéma pour l'initialisation d'un import de données."""
    source: str
    target: Optional[str] = None
    status: Optional[str] = "pending"


class DataImportUpdate(SQLModel):
    """Schéma pour la mise à jour d'un statut d'import."""
    status: Optional[str] = None
    records_imported: Optional[int] = None
    records_skipped: Optional[int] = None
    error_log: Optional[str] = None
    finished_at: Optional[datetime] = None


# --- Read ---

class DataImportRead(SQLModel):
    """Schéma de lecture d'un rapport d'import de données."""
    id: uuid.UUID
    source: str
    target: Optional[str]
    status: str
    records_imported: int
    records_skipped: int
    error_log: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
