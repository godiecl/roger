"""
Database session management for ROGER - Valeria API
"""

from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config.settings import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    poolclass=NullPool if "sqlite" in settings.database_url else None
)

# Enable FK constraints for SQLite
if "sqlite" in settings.database_url:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    from app.infrastructure.database.base import Base

    # ── Existing models ───────────────────────────────────────────────────────
    import app.features.authenticate.infrastructure.persistence.user_model  # noqa
    import app.features.view_images.infrastructure.persistence.image_model  # noqa
    import app.features.generate_narrative.infrastructure.persistence.narrative_model  # noqa
    import app.features.manage_projects.infrastructure.persistence.project_model  # noqa
    import app.features.manage_projects.infrastructure.persistence.project_message_model  # noqa
    import app.features.manage_projects.infrastructure.persistence.project_invitation_model  # noqa

    # ── New models ────────────────────────────────────────────────────────────
    import app.features.archive.infrastructure.persistence.archive_model  # noqa
    import app.features.taxonomy.infrastructure.persistence.taxonomy_model  # noqa
    import app.features.tagging.infrastructure.persistence.tag_model  # noqa
    import app.features.contributions.infrastructure.persistence.contribution_model  # noqa
    import app.features.analysis.infrastructure.persistence.analysis_model  # noqa
    import app.features.detect_objects.infrastructure.persistence.detection_model  # noqa
    import app.features.cluster_images.infrastructure.persistence.cluster_model  # noqa
    import app.features.generate_timeline.infrastructure.persistence.timeline_model  # noqa
    import app.features.generate_context.infrastructure.persistence.context_model  # noqa
    import app.features.generate_context.infrastructure.persistence.like_model  # noqa
    import app.features.generate_context.infrastructure.persistence.report_model  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
