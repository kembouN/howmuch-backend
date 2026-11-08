# Guide Exhaustif : Configuration d'un Projet FastAPI en Production (et Analyse de l'Architecture HowMuch)

Ce document détaille l'ensemble des principes, composants et bonnes pratiques régissant la configuration d'un projet **FastAPI**, tant sur le plan théorique que sur l'implémentation concrète réalisée dans notre projet **HowMuch & Health**.

---

## Sommaire

1. [Introduction et Philosophie de FastAPI](#1-introduction-et-philosophie-de-fastapi)
2. [Arborescence et Modularité (Clean Architecture)](#2-arborescence-et-modularité-clean-architecture)
3. [Configuration & Variables d'Environnement (12-Factor App)](#3-configuration--variables-denvironnement-12-factor-app)
4. [Couche Base de Données : Moteur, Sessions et Dialectes PostgreSQL](#4-couche-base-de-données--moteur-sessions-et-dialectes-postgresql)
5. [Modélisation Hybride avec SQLModel](#5-modélisation-hybride-avec-sqlmodel)
6. [Sécurité, Cryptographie & Authentification (Argon2 & JWT)](#6-sécurité-cryptographie--authentification-argon2--jwt)
7. [Gestion des CORS (Cross-Origin Resource Sharing)](#7-gestion-des-cors-cross-origin-resource-sharing)
8. [Cycle de Vie de l'Application : Gestionnaire Lifespan](#8-cycle-de-vie-de-lapplication--gestionnaire-lifespan)
9. [Schémas, Validation Pydantic et Anti-Patterns à éviter](#9-schémas-validation-pydantic-et-anti-patterns-à-éviter)
10. [Architecture en Couches : Repositories, Services & Injection de Dépendances](#10-architecture-en-couches--repositories-services--injection-de-dépendances)
11. [Guide Opérationnel du Projet HowMuch](#11-guide-opérationnel-du-projet-howmuch)

---

## 1. Introduction et Philosophie de FastAPI

FastAPI est un framework web Python moderne, ultra-rapide et fortement typé, reposant sur deux piliers majeurs :

- **Starlette** : Pour le routage HTTP, les requêtes/réponses WebSockets, les middlewares et la compatibilité **ASGI** (*Asynchronous Server Gateway Interface*).
- **Pydantic** : Pour la validation des données, la sérialisation/désérialisation JSON et la génération automatique des spécifications **OpenAPI (Swagger)** et **JSON Schema**.

### Concurrence : `async def` vs `def` synchrone
FastAPI résout l'un des plus grands dilemmes de Python :
- Si vous déclarez une route avec `async def`, FastAPI l'exécute directement dans la boucle d'événements asyncio (*Event Loop*). Idéal pour les opérations d'I/O non-bloquantes (requêtes HTTP via `httpx`, drivers async comme `asyncpg`).
- Si vous déclarez une route avec un simple `def`, FastAPI l'exécute dans un **thread pool séparé** (*AnyIO worker thread*). Cela garantit que les opérations synchrones et bloquantes (comme le driver `psycopg2` ou le calcul cryptographique Argon2) **ne bloquent pas la boucle d'événements principale**.

---

## 2. Arborescence et Modularité (Clean Architecture)

Pour éviter le syndrome du fichier unique ingérable (`spaghetti code`), un projet FastAPI de niveau production sépare rigoureusement les responsabilités :

```text
howmuch_backend/
├── .env                       # Variables d'environnement locales (non commité)
├── requirements.txt           # Dépendances Python versionnées
├── main.py                    # Point d'entrée pour Uvicorn
├── app/
│   ├── __init__.py
│   ├── main.py                # Instance FastAPI, middlewares, montage des routes
│   ├── core/                  # Configuration et primitives transverses
│   │   ├── config.py          # Classe Settings Pydantic (chargement .env)
│   │   ├── database.py        # Moteur Engine, SessionFactory, get_session
│   │   └── security.py        # Argon2, JWT (création/décodage)
│   ├── models/                # Modèles de base de données (Tables SQLModel)
│   │   ├── base_model.py      # Classe abstraite (UUID id, created_at, updated_at)
│   │   ├── user_account.py    # Entité Utilisateur et Rôles
│   │   ├── location.py        # Villes, Quartiers, Coordonnées GPS
│   │   ├── merchant.py        # Marchés, Supermarchés, Pharmacies de garde
│   │   ├── product.py         # Produits alimentaires et Médicaments
│   │   ├── price_record.py    # Relevés spatio-temporels de prix
│   │   └── data_import.py     # Journal d'audit ETL & Scrapers
│   ├── schemas/               # DTO (Data Transfer Objects) Pydantic
│   │   ├── user_account.py    # Request/Response DTOs (Register, Login, Token)
│   │   ├── product.py
│   │   ├── price_record.py
│   │   └── ...
│   ├── repositories/          # Accès aux données (requêtes SQLModel/SQLAlchemy)
│   │   ├── base_repository.py # CRUD générique
│   │   └── user_account_repository.py
│   ├── services/              # Logique métier pure
│   │   └── auth_service.py    # Orchestration inscription, vérification, token
│   ├── api/                   # Couche Contrôleurs / Endpoints HTTP
│   │   ├── deps.py            # Dépendances FastAPI (get_current_user, etc.)
│   │   ├── auth.py            # Routes /api/auth (register, login, me)
│   │   └── __init__.py        # Agrégation du router global /api
│   └── etl/                   # Pipelines d'ingestion (CSV WFP & Web Scraping)
└── tests/                     # Suite de tests automatisés
    └── test_auth.py
```

---

## 3. Configuration & Variables d'Environnement (12-Factor App)

Selon le principe III des **12-Factor Apps**, toute la configuration susceptible de changer entre environnements (développement, staging, production) doit être externalisée dans des variables d'environnement.

### Le rôle de `pydantic-settings`
Dans `app/core/config.py` :
```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "HowMuch & Health"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/howmuch_db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### Pourquoi `@lru_cache` ?
L'accès au disque pour parser le fichier `.env` à chaque requête détruirait les performances. Le décorateur `@lru_cache` transforme `get_settings()` en **Singleton mémoïsé** : la configuration n'est chargée qu'une seule fois au démarrage.

---

## 4. Couche Base de Données : Moteur, Sessions et Dialectes PostgreSQL

Le fichier `app/core/database.py` configure la connexion avec la base PostgreSQL.

### Les Dialectes SQLAlchemy pour PostgreSQL
Un piège fréquent réside dans le préfixe de protocole :
- `postgresql://` : Dialecte par défaut (historiquement psycopg2, psycopg 3 en SQLAlchemy 2.0).
- `postgresql+psycopg2://` : Pilote synchrone robuste basé sur C. Requis par les moteurs synchrones `create_engine`.
- `postgresql+asyncpg://` : Pilote asynchrone asyncio. Incompatible avec le `create_engine` synchrone traditionnel.

Dans `app/core/database.py`, nous avons mis en place une fonction de normalisation préventive :
```python
def get_sync_database_url(url: str) -> str:
    """Convertit automatiquement les URL asyncpg si un moteur synchrone est utilisé."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url
```

### Le Connection Pooling (Gestion de Pool)
```python
engine = create_engine(
    sync_db_url,
    echo=settings.DEBUG,     # Affiche les requêtes SQL dans la console en dev
    pool_pre_ping=True,      # Teste la connexion avant de la servir (évite les connexions mortes)
    pool_size=10,            # 10 connexions persistantes maintenues ouvertes
    max_overflow=20,         # Capacité d'emprunt jusqu'à 30 connexions lors des pics
)
```

### Le Générateur de Session (`get_session`)
```python
def get_session():
    with Session(engine) as session:
        yield session
```
Grâce à `yield`, FastAPI injecte la session dans vos fonctions via `Depends(get_session)`. À la fin de la réponse HTTP, FastAPI reprend l'exécution après le `yield` et **ferme automatiquement la session**, garantissant zéro fuite de connexion (*connection leak*).

---

## 5. Modélisation Hybride avec SQLModel

**SQLModel** (conçu par le créateur de FastAPI) réconcilie deux univers qui doublonnaient traditionnellement le code :
1. Les modèles **SQLAlchemy** (représentation relationnelle, tables, clés étrangères).
2. Les modèles **Pydantic** (typage, validation, conversion JSON).

### La classe abstraite commune (`BaseModel`)
Dans `app/models/base_model.py` :
```python
class BaseModel(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
```
Toutes nos entités héritent de cet identifiant unique **UUID v4** (impossible à deviner, parfait pour les systèmes distribués) et de timestamps horodatés en UTC.

### Gestion des clés étrangères
Pour relier `Product` à `UserAccount` :
- `foreign_key="user_account.id"` pointe sur le nom exact de la table SQL (`__tablename__`).
- `Relationship(back_populates="products")` permet l'accès objet bidirectionnel (ex: `user.products`).

---

## 6. Sécurité, Cryptographie & Authentification (Argon2 & JWT)

### Pourquoi Argon2 plutôt que bcrypt ou MD5/SHA256 ?
- **MD5 / SHA256** sont des fonctions de hachage rapides conçues pour l'intégrité de fichiers, **à proscrire absolument** pour les mots de passe (vulnérables aux attaques par force brute sur GPU).
- **Argon2id** est le vainqueur du *Password Hashing Competition* et le standard recommandé par l'OWASP. Il résiste aux attaques matérielles (GPU/ASIC) en configurant simultanément un coût en temps (`time_cost=3`) et un coût en mémoire (`memory_cost=65536` soit 64 Mo de RAM par tentative).

### Les Tokens JWT (JSON Web Tokens)
Dans `app/core/security.py` :
- **En-tête (`header`)** : Algorithme de signature (`HS256`).
- **Charge utile (`payload`)** :
  - `sub` : Identifiant unique de l'utilisateur (`user.id`).
  - `email` : Adresse email.
  - `role` : Rôle (`citizen` ou `admin`).
  - `iat` : Horodatage d'émission.
  - `exp` : Date et heure d'expiration stricte.
- **Signature** : Calculée avec le `SECRET_KEY` privé du serveur. Si un pirate modifie le payload pour se faire passer pour un `admin`, la signature devient invalide et FastAPI rejette la requête immédiatement avec une erreur `401 Unauthorized`.

---

## 7. Gestion des CORS (Cross-Origin Resource Sharing)

Par défaut, les navigateurs interdisent à une application frontend (ex: Vite sur `http://localhost:5173`) d'appeler une API hébergée sur un autre domaine/port (`http://localhost:8000`).

Dans `app/main.py` :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Ce middleware intercepte les requêtes de pré-vérification du navigateur (`OPTIONS preflight requests`) et ajoute les en-têtes nécessaires (`Access-Control-Allow-Origin`, `Access-Control-Allow-Headers`).

---

## 8. Cycle de Vie de l'Application : Gestionnaire Lifespan

Les événements obsolètes `@app.on_event("startup")` sont remplacés par le gestionnaire de contexte asynchrone `lifespan` :

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 1 : Code exécuté AVANT la réception de la première requête
    create_db_and_tables()   # Création automatique des tables SQLModel
    yield
    # Phase 2 : Code exécuté LORS DE L'ARRÊT du serveur
    # Exemple : fermeture de pools de scraping, déconnexion Redis, etc.
```

---

## 9. Schémas, Validation Pydantic et Anti-Patterns à éviter

### ⚠️ L'Anti-Pattern : Exposer directement les modèles SQL en entrée/sortie
Ne retournez **jamais** un modèle de table SQL directement dans une route d'API :
1. **Fuite de données sensibles** : Risque d'exposer `hashed_password` dans la réponse JSON.
2. **Vulnérabilité de sur-assignation (*Mass Assignment*)** : Un utilisateur pourrait injecter `"role": "admin"` ou `"is_blocked": false` si vous désérialisez directement la requête HTTP dans la table.

### La bonne pratique : DTOs spécialisés
- `UserRegisterRequest` : Exige `email`, `password`, `confirm_password` avec validateurs stricts.
- `UserLoginRequest` : Exige `email`, `password`.
- `UserAccountRead` : Expose uniquement les champs publics sécurisés (`id`, `email`, `role`, `is_active`, `created_at`).

---

## 10. Architecture en Couches : Repositories, Services & Injection de Dépendances

Notre projet structure l'exécution d'une requête HTTP en 4 maillons étanches :

```mermaid
flowchart LR
    Client["Client (Frontend / Mobile)"] --> Route["Route HTTP (/api/auth/register)"]
    Route --> Service["Service Layer (AuthService)"]
    Service --> Repo["Repository (UserAccountRepository)"]
    Repo --> DB[("PostgreSQL (howmuch_db)")]
```

1. **Route (`app/api/auth.py`)** : Reçoit la requête HTTP, injecte la session DB via `Depends(get_session)`, délègue au Service et retourne le code HTTP adapté (`201 Created`).
2. **Service (`app/services/auth_service.py`)** : Porte les règles métier (vérifier que l'email n'existe pas, hacher le mot de passe, orchestrer la délivrance du token).
3. **Repository (`app/repositories/user_account_repository.py`)** : Isole les requêtes SQL/SQLModel (`select`, `where`, `insert`, `commit`).
4. **Base de données** : PostgreSQL exécute la persistance.

---

## 11. Guide Opérationnel du Projet HowMuch

### Lancement du serveur en développement
Depuis la racine du projet backend :
```bash
# Activation du venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Démarrage avec rechargement à chaud
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### URLs utiles
- **API Base** : `http://127.0.0.1:8000`
- **Healthcheck** : `http://127.0.0.1:8000/health`
- **Documentation Swagger interactive** : `http://127.0.0.1:8000/docs`
- **Documentation ReDoc alternative** : `http://127.0.0.1:8000/redoc`

### Exécution des tests automatisés
```bash
python tests/test_auth.py
```
Ce script vérifie la validation des formulaires, l'inscription effective en base PostgreSQL, le hachage Argon2, la gestion des doublons, la connexion et l'accès protégé via jeton Bearer JWT.
