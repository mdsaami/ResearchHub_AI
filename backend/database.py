"""
ResearchHub AI – Database Setup
Async SQLAlchemy engine, session factory, and dependency injection.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from backend.config import get_settings

settings = get_settings()

# ── Async Engine ────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

# ── Session Factory ─────────────────────────────
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative Base ────────────────────────────
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ── Dependency ──────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency that provides a database session."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
