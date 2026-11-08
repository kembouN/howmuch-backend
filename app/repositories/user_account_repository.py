from typing import Optional
from sqlmodel import Session, select
from app.models.user_account import UserAccount
from app.repositories.base_repository import BaseRepository


class UserAccountRepository(BaseRepository[UserAccount]):
    """Repository pour les opérations CRUD sur UserAccount."""

    def __init__(self, session: Session):
        super().__init__(UserAccount, session)

    def get_by_email(self, email: str) -> Optional[UserAccount]:
        """Récupère un utilisateur par son email."""
        statement = select(UserAccount).where(UserAccount.email == email)
        return self.session.exec(statement).first()

    def email_exists(self, email: str) -> bool:
        """Vérifie si un email est déjà utilisé."""
        return self.get_by_email(email) is not None

    def increment_report_count(self, user: UserAccount) -> UserAccount:
        """Incrémente le compteur de signalements."""
        user.report_count += 1
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
