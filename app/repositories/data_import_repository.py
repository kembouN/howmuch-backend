from datetime import datetime, timezone
from typing import Sequence, Optional
from sqlmodel import Session, select
from app.models.data_import import DataImport, ImportStatus
from app.repositories.base_repository import BaseRepository


class DataImportRepository(BaseRepository[DataImport]):
    """Repository pour la gestion et l'audit des opérations d'import de données."""

    def __init__(self, session: Session):
        super().__init__(DataImport, session)

    def get_by_source(self, source: str, *, offset: int = 0, limit: int = 100) -> Sequence[DataImport]:
        """Récupère les imports par type de source."""
        statement = (
            select(DataImport)
            .where(DataImport.source == source)
            .order_by(DataImport.started_at.desc())  # type: ignore
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_latest(self) -> Optional[DataImport]:
        """Récupère le dernier import effectué."""
        statement = (
            select(DataImport)
            .order_by(DataImport.started_at.desc())  # type: ignore
            .limit(1)
        )
        return self.session.exec(statement).first()

    def mark_completed(
        self,
        data_import: DataImport,
        imported_count: int,
        skipped_count: int = 0
    ) -> DataImport:
        """Marque l'import comme terminé avec succès."""
        data_import.status = ImportStatus.COMPLETED.value
        data_import.records_imported = imported_count
        data_import.records_skipped = skipped_count
        data_import.finished_at = datetime.now(timezone.utc)
        self.session.add(data_import)
        self.session.commit()
        self.session.refresh(data_import)
        return data_import

    def mark_failed(self, data_import: DataImport, error_message: str) -> DataImport:
        """Marque l'import comme échoué avec journalisation de l'erreur."""
        data_import.status = ImportStatus.FAILED.value
        data_import.error_log = error_message
        data_import.finished_at = datetime.now(timezone.utc)
        self.session.add(data_import)
        self.session.commit()
        self.session.refresh(data_import)
        return data_import
