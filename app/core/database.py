from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings


def get_sync_database_url(url: str) -> str:
    """Assure que l'URL utilise un driver synchrone pour SQLModel/SQLAlchemy."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


sync_db_url = get_sync_database_url(settings.DATABASE_URL)

engine = create_engine(
    sync_db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def create_db_and_tables() -> None:
    """Crée toutes les tables définies avec SQLModel dans PostgreSQL."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency FastAPI pour obtenir une session de base de données."""
    with Session(engine) as session:
        yield session
