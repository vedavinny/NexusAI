"""
Declarative base for all ORM models, plus a helper to create tables.
In production you would use Alembic migrations instead of create_all();
create_all() is fine for a starter/dev project.
"""
from sqlalchemy.orm import DeclarativeBase

from backend.database.session import engine


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create all tables. Import models before calling this so they register on Base.metadata."""
    from backend.models import chat, document, user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
