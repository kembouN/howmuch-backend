from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.user_account import UserAccount
from app.schemas.user_account import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserAccountRead,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Création de compte citoyen et remise du jeton",
)
def register(
    request: UserRegisterRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    """Permet à un utilisateur de créer un compte avec email et mot de passe confirmé.

    Délivre immédiatement un jeton d'accès JWT pour une expérience fluide.
    """
    auth_service = AuthService(session)
    return auth_service.register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authentification et délivrance du jeton",
)
def login(
    request: UserLoginRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    """Authentifie un utilisateur existant avec son adresse email et son mot de passe.

    Renvoie le jeton d'accès JWT ainsi que le profil utilisateur.
    """
    auth_service = AuthService(session)
    return auth_service.authenticate(request)


@router.get(
    "/me",
    response_model=UserAccountRead,
    status_code=status.HTTP_200_OK,
    summary="Profil de l'utilisateur connecté",
)
def get_me(
    current_user: Annotated[UserAccount, Depends(get_current_user)],
) -> UserAccountRead:
    """Renvoie les informations du profil de l'utilisateur actuellement authentifié."""
    return UserAccountRead.model_validate(current_user)
