"""
Alembic environment configuration for ROGER - Valeria
"""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import the Base from your models
from app.infrastructure.database.base import Base
from app.config.settings import settings

# ── Existing models ───────────────────────────────────────────────────────────
from app.features.authenticate.infrastructure.persistence.user_model import UserModel
from app.features.view_images.infrastructure.persistence.image_model import ImageModel, CollectionModel
from app.features.generate_narrative.infrastructure.persistence.narrative_model import NarrativeModel
from app.features.manage_projects.infrastructure.persistence.project_model import (
    ProjectModel, ProjectMemberModel, ProjectCollectionModel, ProjectPhotographModel,
)
from app.features.manage_projects.infrastructure.persistence.project_message_model import ProjectMessageModel

# ── New archive models ────────────────────────────────────────────────────────
from app.features.archive.infrastructure.persistence.archive_model import (
    BoxModel, RollModel, PhotographModel, PhotographFileModel,
)

# ── New taxonomy models ───────────────────────────────────────────────────────
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrTechnicalMetadataModel,
    AttrChronologyDatingModel,
    AttrGeographicReferenceModel,
    AttrEnvironmentalSpatialModel,
)

# ── New tagging models ────────────────────────────────────────────────────────
from app.features.tagging.infrastructure.persistence.tag_model import TagModel, PhotographTagModel

# ── New contribution models ───────────────────────────────────────────────────
from app.features.contributions.infrastructure.persistence.contribution_model import MetadataContributionModel

# ── New analysis models ───────────────────────────────────────────────────────
from app.features.analysis.infrastructure.persistence.analysis_model import AnalysisJobModel, ExperimentModel

# ── New feature models (detect_objects, cluster_images, generate_timeline) ────
from app.features.detect_objects.infrastructure.persistence.detection_model import (
    ObjectDetectionModel, DetectedObjectModel,
)
from app.features.cluster_images.infrastructure.persistence.cluster_model import (
    ClusteringJobModel, ClusterModel,
)
from app.features.generate_timeline.infrastructure.persistence.timeline_model import (
    TimelineModel, TimelineEventModel,
)

# ── Community engagement models (generate_context) ────────────────────────────
from app.features.generate_context.infrastructure.persistence.context_model import ImageContextModel
from app.features.generate_context.infrastructure.persistence.like_model import ContentLikeModel
from app.features.generate_context.infrastructure.persistence.report_model import ContentReportModel

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with the one from settings
config.set_main_option('sqlalchemy.url', settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
