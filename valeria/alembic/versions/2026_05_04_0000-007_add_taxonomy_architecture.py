"""add taxonomy architecture

Revision ID: 007
Revises: 006
Create Date: 2026-05-04 00:00:00.000000

Adds:
- New columns to users (rut_passport, first_name, last_name, phone, nationality,
  gender, affiliation, organization, position, expiry_date)
- New columns to collections (slug, photographer_name, origin_country,
  date_range_from, date_range_to, is_public, cover_image_path, license, copyright_notes)
- boxes, rolls, photographs, photograph_files
- attr_technical_metadata, attr_chronology_dating,
  attr_geographic_reference, attr_environmental_spatial
- tags, photograph_tags
- metadata_contributions
- analysis_jobs, experiments
- project_collections, project_photographs
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── 1. Extend users ───────────────────────────────────────────────────────
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("first_name", sa.String(150), nullable=True))
        batch_op.add_column(sa.Column("last_name", sa.String(150), nullable=True))
        batch_op.add_column(sa.Column("rut_passport", sa.String(30), nullable=True))
        batch_op.add_column(sa.Column("phone", sa.String(30), nullable=True))
        batch_op.add_column(sa.Column("nationality", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("gender", sa.String(50), nullable=True))
        batch_op.add_column(sa.Column("affiliation", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("organization", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("position", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True))

    # ── 2. Extend collections ─────────────────────────────────────────────────
    with op.batch_alter_table("collections") as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("photographer_name", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("origin_country", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("date_range_from", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("date_range_to", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("cover_image_path", sa.String(512), nullable=True))
        batch_op.add_column(sa.Column("license", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("copyright_notes", sa.Text(), nullable=True))
        batch_op.create_index("ix_collections_slug", ["slug"], unique=True)

    # ── 3. boxes ──────────────────────────────────────────────────────────────
    op.create_table(
        "boxes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("box_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("location_in_archive", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_boxes_id", "boxes", ["id"])
    op.create_index("ix_boxes_collection_id", "boxes", ["collection_id"])

    # ── 4. rolls ──────────────────────────────────────────────────────────────
    op.create_table(
        "rolls",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("box_id", sa.Integer(), nullable=False),
        sa.Column("general_number", sa.Integer(), nullable=True),
        sa.Column("internal_number", sa.Integer(), nullable=True),
        sa.Column("og_number", sa.Integer(), nullable=True),
        sa.Column("strip_letter", sa.String(5), nullable=True),
        sa.Column("name", sa.String(512), nullable=True),
        sa.Column("image_type", sa.String(10), nullable=True),
        sa.Column("support", sa.String(10), nullable=True),
        sa.Column("physical_status", sa.String(10), nullable=True),
        sa.Column("color_mode", sa.String(10), nullable=True),
        sa.Column("frame_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["box_id"], ["boxes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rolls_id", "rolls", ["id"])
    op.create_index("ix_rolls_box_id", "rolls", ["box_id"])
    op.create_index("ix_rolls_general_number", "rolls", ["general_number"])

    # ── 5. photographs ────────────────────────────────────────────────────────
    op.create_table(
        "photographs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("roll_id", sa.Integer(), nullable=False),
        sa.Column("frame_number", sa.Integer(), nullable=True),
        sa.Column("identifier", sa.String(100), nullable=True),
        sa.Column("physical_location_ref", sa.String(512), nullable=True),
        sa.Column("digitalization_date", sa.Date(), nullable=True),
        sa.Column("width_px", sa.Integer(), nullable=True),
        sa.Column("height_px", sa.Integer(), nullable=True),
        sa.Column("color_depth", sa.Integer(), nullable=True),
        sa.Column("resolution_dpi", sa.Float(), nullable=True),
        sa.Column("internal_cronology", sa.String(255), nullable=True),
        sa.Column("license", sa.String(255), nullable=True),
        sa.Column("copyright_notes", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("digitalized_by", sa.Integer(), nullable=True),
        sa.Column("responsible_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["roll_id"], ["rolls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["digitalized_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["responsible_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_photographs_id", "photographs", ["id"])
    op.create_index("ix_photographs_roll_id", "photographs", ["roll_id"])
    op.create_index("ix_photographs_identifier", "photographs", ["identifier"])
    op.create_index("ix_photographs_is_public", "photographs", ["is_public"])

    # ── 6. photograph_files ───────────────────────────────────────────────────
    op.create_table(
        "photograph_files",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("is_master", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_photograph_files_id", "photograph_files", ["id"])
    op.create_index("ix_photograph_files_photograph_id", "photograph_files", ["photograph_id"])

    # ── 7. attr_technical_metadata ────────────────────────────────────────────
    op.create_table(
        "attr_technical_metadata",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("film_format", sa.String(50), nullable=True),
        sa.Column("manufacturer", sa.String(100), nullable=True),
        sa.Column("emulsion_type", sa.String(100), nullable=True),
        sa.Column("iso_sensitivity", sa.String(20), nullable=True),
        sa.Column("mounting_marks", sa.String(255), nullable=True),
        sa.Column("scanning_artifacts", sa.String(255), nullable=True),
        sa.Column("physical_status", sa.String(20), nullable=True),
        sa.Column("exposure", sa.String(50), nullable=True),
        sa.Column("diaphragm_aperture", sa.String(50), nullable=True),
        sa.Column("lens_optical", sa.String(100), nullable=True),
        sa.Column("camera_settings", sa.String(255), nullable=True),
        sa.Column("deterioration_notes", sa.Text(), nullable=True),
        sa.Column("digitizer_person", sa.String(255), nullable=True),
        sa.Column("is_estimated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("analysis_provider", sa.String(100), nullable=True),
        sa.Column("provider_version", sa.String(50), nullable=True),
        sa.Column("confidence_level", sa.Float(), nullable=True),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attr_technical_metadata_id", "attr_technical_metadata", ["id"])
    op.create_index("ix_attr_technical_metadata_photograph_id", "attr_technical_metadata", ["photograph_id"])
    op.create_index("ix_attr_technical_metadata_status", "attr_technical_metadata", ["status"])

    # ── 8. attr_chronology_dating ─────────────────────────────────────────────
    op.create_table(
        "attr_chronology_dating",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("source_type", sa.String(20), nullable=False, server_default="ai"),
        sa.Column("date_type", sa.String(20), nullable=True),
        sa.Column("precise_date", sa.Date(), nullable=True),
        sa.Column("date_from", sa.Date(), nullable=True),
        sa.Column("date_to", sa.Date(), nullable=True),
        sa.Column("date_hypothesis", sa.Text(), nullable=True),
        sa.Column("verification_source", sa.String(255), nullable=True),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("visual_evidence_notes", sa.Text(), nullable=True),
        sa.Column("analysis_provider", sa.String(100), nullable=True),
        sa.Column("provider_version", sa.String(50), nullable=True),
        sa.Column("confidence_level", sa.Float(), nullable=True),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attr_chronology_dating_id", "attr_chronology_dating", ["id"])
    op.create_index("ix_attr_chronology_dating_photograph_id", "attr_chronology_dating", ["photograph_id"])
    op.create_index("ix_attr_chronology_dating_status", "attr_chronology_dating", ["status"])

    # ── 9. attr_geographic_reference ──────────────────────────────────────────
    op.create_table(
        "attr_geographic_reference",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("source_type", sa.String(20), nullable=False, server_default="ai"),
        sa.Column("location_type", sa.String(20), nullable=True),
        sa.Column("geographic_location", sa.String(512), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("location_radius_km", sa.Float(), nullable=True),
        sa.Column("signage_found", sa.Text(), nullable=True),
        sa.Column("architectural_landmarks", sa.Text(), nullable=True),
        sa.Column("landscape_features", sa.Text(), nullable=True),
        sa.Column("analysis_provider", sa.String(100), nullable=True),
        sa.Column("provider_version", sa.String(50), nullable=True),
        sa.Column("confidence_level", sa.Float(), nullable=True),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attr_geographic_reference_id", "attr_geographic_reference", ["id"])
    op.create_index("ix_attr_geographic_reference_photograph_id", "attr_geographic_reference", ["photograph_id"])
    op.create_index("ix_attr_geographic_reference_status", "attr_geographic_reference", ["status"])

    # ── 10. attr_environmental_spatial ────────────────────────────────────────
    op.create_table(
        "attr_environmental_spatial",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("source_type", sa.String(20), nullable=False, server_default="ai"),
        sa.Column("setting_type", sa.String(20), nullable=True),
        sa.Column("specific_typology", sa.String(255), nullable=True),
        sa.Column("conservation_state", sa.String(20), nullable=True),
        sa.Column("human_env_relationship", sa.Text(), nullable=True),
        sa.Column("analysis_provider", sa.String(100), nullable=True),
        sa.Column("provider_version", sa.String(50), nullable=True),
        sa.Column("confidence_level", sa.Float(), nullable=True),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attr_environmental_spatial_id", "attr_environmental_spatial", ["id"])
    op.create_index("ix_attr_environmental_spatial_photograph_id", "attr_environmental_spatial", ["photograph_id"])
    op.create_index("ix_attr_environmental_spatial_status", "attr_environmental_spatial", ["status"])

    # ── 11. tags ──────────────────────────────────────────────────────────────
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "collection_id", name="uq_tag_name_collection"),
    )
    op.create_index("ix_tags_id", "tags", ["id"])
    op.create_index("ix_tags_name", "tags", ["name"])
    op.create_index("ix_tags_collection_id", "tags", ["collection_id"])

    # ── 12. photograph_tags ───────────────────────────────────────────────────
    op.create_table(
        "photograph_tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("originated_from_attribute", sa.Integer(), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("photograph_id", "tag_id", "source", name="uq_photograph_tag_source"),
    )
    op.create_index("ix_photograph_tags_photograph_id", "photograph_tags", ["photograph_id"])
    op.create_index("ix_photograph_tags_tag_id", "photograph_tags", ["tag_id"])
    op.create_index("ix_photograph_tags_status", "photograph_tags", ["status"])

    # ── 13. metadata_contributions ────────────────────────────────────────────
    op.create_table(
        "metadata_contributions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("contributor_id", sa.Integer(), nullable=True),
        sa.Column("attribute_type", sa.String(30), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("proposed_value", sa.Text(), nullable=False),
        sa.Column("evidence_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contributor_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metadata_contributions_id", "metadata_contributions", ["id"])
    op.create_index("ix_metadata_contributions_photograph_id", "metadata_contributions", ["photograph_id"])
    op.create_index("ix_metadata_contributions_status", "metadata_contributions", ["status"])
    op.create_index("ix_metadata_contributions_attribute_type", "metadata_contributions", ["attribute_type"])

    # ── 14. analysis_jobs ─────────────────────────────────────────────────────
    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("attribute_type", sa.String(30), nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("tool_version", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("triggered_by", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["triggered_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_jobs_id", "analysis_jobs", ["id"])
    op.create_index("ix_analysis_jobs_photograph_id", "analysis_jobs", ["photograph_id"])
    op.create_index("ix_analysis_jobs_status", "analysis_jobs", ["status"])
    op.create_index("ix_analysis_jobs_attribute_type", "analysis_jobs", ["attribute_type"])

    # ── 15. experiments ───────────────────────────────────────────────────────
    op.create_table(
        "experiments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("attribute_type", sa.String(30), nullable=False),
        sa.Column("conducted_by", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("analysis_job_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="planned"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conducted_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["analysis_job_id"], ["analysis_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_experiments_id", "experiments", ["id"])
    op.create_index("ix_experiments_photograph_id", "experiments", ["photograph_id"])
    op.create_index("ix_experiments_conducted_by", "experiments", ["conducted_by"])
    op.create_index("ix_experiments_project_id", "experiments", ["project_id"])
    op.create_index("ix_experiments_status", "experiments", ["status"])

    # ── 16. project_collections ───────────────────────────────────────────────
    op.create_table(
        "project_collections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "collection_id", name="uq_project_collection"),
    )
    op.create_index("ix_project_collections_project_id", "project_collections", ["project_id"])
    op.create_index("ix_project_collections_collection_id", "project_collections", ["collection_id"])

    # ── 17. project_photographs ───────────────────────────────────────────────
    op.create_table(
        "project_photographs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("photograph_id", sa.Integer(), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["photograph_id"], ["photographs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "photograph_id", name="uq_project_photograph"),
    )
    op.create_index("ix_project_photographs_project_id", "project_photographs", ["project_id"])
    op.create_index("ix_project_photographs_photograph_id", "project_photographs", ["photograph_id"])


def downgrade() -> None:
    op.drop_table("project_photographs")
    op.drop_table("project_collections")
    op.drop_table("experiments")
    op.drop_table("analysis_jobs")
    op.drop_table("metadata_contributions")
    op.drop_table("photograph_tags")
    op.drop_table("tags")
    op.drop_table("attr_environmental_spatial")
    op.drop_table("attr_geographic_reference")
    op.drop_table("attr_chronology_dating")
    op.drop_table("attr_technical_metadata")
    op.drop_table("photograph_files")
    op.drop_table("photographs")
    op.drop_table("rolls")
    op.drop_table("boxes")

    with op.batch_alter_table("collections") as batch_op:
        batch_op.drop_index("ix_collections_slug")
        batch_op.drop_column("copyright_notes")
        batch_op.drop_column("license")
        batch_op.drop_column("cover_image_path")
        batch_op.drop_column("is_public")
        batch_op.drop_column("date_range_to")
        batch_op.drop_column("date_range_from")
        batch_op.drop_column("origin_country")
        batch_op.drop_column("photographer_name")
        batch_op.drop_column("slug")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("expiry_date")
        batch_op.drop_column("position")
        batch_op.drop_column("organization")
        batch_op.drop_column("affiliation")
        batch_op.drop_column("gender")
        batch_op.drop_column("nationality")
        batch_op.drop_column("phone")
        batch_op.drop_column("rut_passport")
        batch_op.drop_column("last_name")
        batch_op.drop_column("first_name")
