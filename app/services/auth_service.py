from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user_account import UserAccount, UserRole
from app.repositories.user_account_repository import UserAccountRepository
from app.schemas.user_account import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserAccountRead,
)


class AuthService:
    """Service gérant la logique métier d'inscription et d'authentification."""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserAccountRepository(session)

    def register(self, request: UserRegisterRequest) -> TokenResponse:
        """Crée un nouveau compte utilisateur et délivre immédiatement un jeton JWT."""
        # 1. Vérifier si l'email existe déjà
        if self.user_repo.email_exists(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une adresse compte avec cet email existe déjà.",
            )

        # 2. Hacher le mot de passe avec Argon2
        hashed_pwd = hash_password(request.password)

        # 3. Créer l'entité UserAccount (par défaut citoyen)
        new_user = UserAccount(
            email=request.email,
            hashed_password=hashed_pwd,
            role=UserRole.CITIZEN.value,
            is_active=True,
            is_blocked=False,
            report_count=0,
        )

        user = self.user_repo.create(new_user)

        # 4. Générer le jeton JWT
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "role": user.role},
        )

        user_read = UserAccountRead.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_read,
        )

    def authenticate(self, request: UserLoginRequest) -> TokenResponse:
        """Vérifie les identifiants de l'utilisateur et délivre un jeton JWT."""
        user = self.user_repo.get_by_email(request.email)

        # 1. Vérifier l'existence et le mot de passe
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Vérifier l'état du compte
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce compte utilisateur est inactif.",
            )

        if user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce compte utilisateur a été bloqué.",
            )

        # 3. Générer le jeton JWT
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "role": user.role},
        )

        user_read = UserAccountRead.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_read,
        )
