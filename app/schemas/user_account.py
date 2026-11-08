import re
import uuid
from datetime import datetime
from typing import Optional
from pydantic import field_validator, model_validator
from sqlmodel import SQLModel

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# --- Register / Login / Token Schemas ---

class UserRegisterRequest(SQLModel):
    """Schéma de création de compte utilisateur avec confirmation de mot de passe."""
    email: str
    password: str
    confirm_password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean_email = v.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            raise ValueError("Format d'adresse email invalide.")
        return clean_email

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit comporter au moins 6 caractères.")
        return v

    @model_validator(mode="after")
    def verify_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return self


class UserLoginRequest(SQLModel):
    """Schéma d'authentification (connexion)."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()


class UserAccountRead(SQLModel):
    """Schéma de lecture publique d'un utilisateur."""
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    is_blocked: bool
    report_count: int
    created_at: datetime
    updated_at: datetime


class TokenResponse(SQLModel):
    """Réponse contenant le jeton d'accès JWT et les informations de profil."""
    access_token: str
    token_type: str = "bearer"
    user: UserAccountRead


# --- Generic Create / Update Schemas ---

class UserAccountCreate(SQLModel):
    """Schéma interne pour la création d'un utilisateur."""
    email: str
    password: str
    role: Optional[str] = "citizen"


class UserAccountUpdate(SQLModel):
    """Schéma pour la mise à jour d'un profil utilisateur."""
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None
