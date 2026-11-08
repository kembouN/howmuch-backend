from datetime import datetime, timezone
import uuid as uuid_pkg
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """Abstract base model with id, created_at, and updated_at.

    Not a table itself — subclasses must set `table=True`.
    """

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
