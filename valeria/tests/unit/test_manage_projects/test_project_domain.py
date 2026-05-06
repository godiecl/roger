"""
Unit tests for manage_projects domain entities.
"""

import pytest
from datetime import date

from app.features.manage_projects.domain.project import Project, ProjectMember
from app.features.manage_projects.domain.project_role import ProjectRole


class TestProjectRole:
    """Tests for ProjectRole enum."""

    def test_role_values(self):
        assert ProjectRole.LIDER == "lider"
        assert ProjectRole.INVESTIGADOR == "investigador"
        assert ProjectRole.COLABORADOR == "colaborador"
        assert ProjectRole.OBSERVADOR == "observador"

    def test_lider_can_manage_members(self):
        assert ProjectRole.can_manage_members(ProjectRole.LIDER) is True

    def test_non_lider_cannot_manage_members(self):
        assert ProjectRole.can_manage_members(ProjectRole.INVESTIGADOR) is False
        assert ProjectRole.can_manage_members(ProjectRole.COLABORADOR) is False
        assert ProjectRole.can_manage_members(ProjectRole.OBSERVADOR) is False

    def test_edit_permissions(self):
        assert ProjectRole.can_edit_project(ProjectRole.LIDER) is True
        assert ProjectRole.can_edit_project(ProjectRole.INVESTIGADOR) is True
        assert ProjectRole.can_edit_project(ProjectRole.COLABORADOR) is False
        assert ProjectRole.can_edit_project(ProjectRole.OBSERVADOR) is False

    def test_share_content_permissions(self):
        assert ProjectRole.can_share_content(ProjectRole.LIDER) is True
        assert ProjectRole.can_share_content(ProjectRole.INVESTIGADOR) is True
        assert ProjectRole.can_share_content(ProjectRole.COLABORADOR) is True
        assert ProjectRole.can_share_content(ProjectRole.OBSERVADOR) is False

    def test_all_roles_can_view(self):
        for role in ProjectRole:
            assert ProjectRole.can_view_content(role) is True


class TestProject:
    """Tests for Project entity."""

    def test_create_project(self):
        project = Project(
            name="Test Project",
            description="A test research project",
            owner_id=1
        )
        assert project.name == "Test Project"
        assert project.description == "A test research project"
        assert project.owner_id == 1
        assert project.is_active is True

    def test_project_with_dates(self):
        project = Project(
            name="Dated Project",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            owner_id=1
        )
        assert project.start_date == date(2026, 1, 1)
        assert project.end_date == date(2026, 12, 31)

    def test_empty_name_raises_error(self):
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            Project(name="", owner_id=1)

    def test_blank_name_raises_error(self):
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            Project(name="   ", owner_id=1)

    def test_long_name_raises_error(self):
        with pytest.raises(ValueError, match="cannot exceed 255 characters"):
            Project(name="A" * 256, owner_id=1)

    def test_end_before_start_raises_error(self):
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            Project(
                name="Invalid Dates",
                start_date=date(2026, 12, 1),
                end_date=date(2026, 1, 1),
                owner_id=1
            )

    def test_is_owner(self):
        project = Project(name="Test", owner_id=42)
        assert project.is_owner(42) is True
        assert project.is_owner(99) is False

    def test_activate_deactivate(self):
        project = Project(name="Test", owner_id=1)
        project.deactivate()
        assert project.is_active is False
        project.activate()
        assert project.is_active is True


class TestProjectMember:
    """Tests for ProjectMember entity."""

    def test_create_member(self):
        member = ProjectMember(
            project_id=1,
            user_id=2,
            role=ProjectRole.INVESTIGADOR
        )
        assert member.project_id == 1
        assert member.user_id == 2
        assert member.role == ProjectRole.INVESTIGADOR

    def test_default_role_is_observador(self):
        member = ProjectMember(project_id=1, user_id=2)
        assert member.role == ProjectRole.OBSERVADOR

    def test_lider_can_manage_members(self):
        member = ProjectMember(
            project_id=1, user_id=2, role=ProjectRole.LIDER
        )
        assert member.can_manage_members() is True

    def test_observador_cannot_manage_members(self):
        member = ProjectMember(
            project_id=1, user_id=2, role=ProjectRole.OBSERVADOR
        )
        assert member.can_manage_members() is False

    def test_change_role(self):
        member = ProjectMember(
            project_id=1, user_id=2, role=ProjectRole.OBSERVADOR
        )
        member.change_role(ProjectRole.INVESTIGADOR)
        assert member.role == ProjectRole.INVESTIGADOR
