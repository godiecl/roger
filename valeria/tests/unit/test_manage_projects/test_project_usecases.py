"""
Unit tests for manage_projects use cases.
"""

import pytest
from unittest.mock import AsyncMock

from app.features.manage_projects.domain.project import Project, ProjectMember
from app.features.manage_projects.domain.project_role import ProjectRole
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.application.create_project_usecase import (
    CreateProjectUseCase
)
from app.features.manage_projects.application.get_project_usecase import (
    GetProjectUseCase
)
from app.features.manage_projects.application.update_project_usecase import (
    UpdateProjectUseCase
)
from app.features.manage_projects.application.delete_project_usecase import (
    DeleteProjectUseCase
)
from app.features.manage_projects.application.add_member_usecase import (
    AddMemberUseCase
)
from app.features.manage_projects.application.remove_member_usecase import (
    RemoveMemberUseCase
)
from app.features.manage_projects.application.list_members_usecase import (
    ListMembersUseCase
)
from app.features.manage_projects.application.list_projects_usecase import (
    ListProjectsUseCase
)
from app.shared.domain.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError,
    BusinessRuleViolationError
)


@pytest.fixture
def mock_repo():
    """Create a mock project repository."""
    return AsyncMock(spec=IProjectRepository)


class TestCreateProjectUseCase:

    async def test_create_project_success(self, mock_repo):
        created_project = Project(
            id=1, name="Test Project", owner_id=1, description="Desc"
        )
        mock_repo.create.return_value = created_project
        mock_repo.add_member.return_value = ProjectMember(
            id=1, project_id=1, user_id=1, role=ProjectRole.LIDER
        )

        usecase = CreateProjectUseCase(mock_repo)
        result = await usecase.execute(
            name="Test Project",
            owner_id=1,
            description="Desc"
        )

        assert result.name == "Test Project"
        assert result.owner_id == 1
        mock_repo.create.assert_called_once()
        mock_repo.add_member.assert_called_once()

    async def test_create_project_adds_owner_as_lider(self, mock_repo):
        created_project = Project(id=1, name="Test", owner_id=5)
        mock_repo.create.return_value = created_project
        mock_repo.add_member.return_value = ProjectMember(
            id=1, project_id=1, user_id=5, role=ProjectRole.LIDER
        )

        usecase = CreateProjectUseCase(mock_repo)
        await usecase.execute(name="Test", owner_id=5)

        # Verify add_member was called with LIDER role
        call_args = mock_repo.add_member.call_args[0][0]
        assert call_args.user_id == 5
        assert call_args.role == ProjectRole.LIDER

    async def test_create_project_invalid_name(self, mock_repo):
        usecase = CreateProjectUseCase(mock_repo)
        with pytest.raises(ValidationError):
            await usecase.execute(name="", owner_id=1)


class TestGetProjectUseCase:

    async def test_get_project_as_owner(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.return_value = None

        usecase = GetProjectUseCase(mock_repo)
        result = await usecase.execute(project_id=1, user_id=1)

        assert result.id == 1

    async def test_get_project_as_member(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        member = ProjectMember(
            id=1, project_id=1, user_id=2, role=ProjectRole.INVESTIGADOR
        )
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.return_value = member

        usecase = GetProjectUseCase(mock_repo)
        result = await usecase.execute(project_id=1, user_id=2)

        assert result.id == 1

    async def test_get_project_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None

        usecase = GetProjectUseCase(mock_repo)
        with pytest.raises(EntityNotFoundError):
            await usecase.execute(project_id=999, user_id=1)

    async def test_get_project_no_access(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.return_value = None

        usecase = GetProjectUseCase(mock_repo)
        with pytest.raises(PermissionDeniedError):
            await usecase.execute(project_id=1, user_id=99)


class TestDeleteProjectUseCase:

    async def test_delete_by_owner(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        mock_repo.get_by_id.return_value = project
        mock_repo.delete.return_value = True

        usecase = DeleteProjectUseCase(mock_repo)
        result = await usecase.execute(project_id=1, user_id=1)

        assert result is True

    async def test_delete_by_non_owner_raises(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        mock_repo.get_by_id.return_value = project

        usecase = DeleteProjectUseCase(mock_repo)
        with pytest.raises(PermissionDeniedError):
            await usecase.execute(project_id=1, user_id=2)


class TestAddMemberUseCase:

    async def test_add_member_by_lider(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        lider = ProjectMember(
            id=1, project_id=1, user_id=1, role=ProjectRole.LIDER
        )
        new_member = ProjectMember(
            id=2, project_id=1, user_id=5, role=ProjectRole.INVESTIGADOR
        )
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.side_effect = [lider, None]
        mock_repo.add_member.return_value = new_member

        usecase = AddMemberUseCase(mock_repo)
        result = await usecase.execute(
            project_id=1,
            user_id=5,
            role=ProjectRole.INVESTIGADOR,
            requesting_user_id=1
        )

        assert result.user_id == 5
        assert result.role == ProjectRole.INVESTIGADOR

    async def test_add_member_already_exists(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        lider = ProjectMember(
            id=1, project_id=1, user_id=1, role=ProjectRole.LIDER
        )
        existing = ProjectMember(
            id=2, project_id=1, user_id=5, role=ProjectRole.OBSERVADOR
        )
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.side_effect = [lider, existing]

        usecase = AddMemberUseCase(mock_repo)
        with pytest.raises(BusinessRuleViolationError):
            await usecase.execute(
                project_id=1,
                user_id=5,
                role=ProjectRole.INVESTIGADOR,
                requesting_user_id=1
            )

    async def test_add_member_by_non_lider_raises(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        non_lider = ProjectMember(
            id=1, project_id=1, user_id=2, role=ProjectRole.COLABORADOR
        )
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.return_value = non_lider

        usecase = AddMemberUseCase(mock_repo)
        with pytest.raises(PermissionDeniedError):
            await usecase.execute(
                project_id=1,
                user_id=5,
                role=ProjectRole.OBSERVADOR,
                requesting_user_id=2
            )


class TestRemoveMemberUseCase:

    async def test_remove_member_success(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        lider = ProjectMember(
            id=1, project_id=1, user_id=1, role=ProjectRole.LIDER
        )
        target = ProjectMember(
            id=2, project_id=1, user_id=5, role=ProjectRole.OBSERVADOR
        )
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.side_effect = [lider, target]
        mock_repo.remove_member.return_value = True

        usecase = RemoveMemberUseCase(mock_repo)
        result = await usecase.execute(
            project_id=1, user_id=5, requesting_user_id=1
        )

        assert result is True

    async def test_remove_owner_raises(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        mock_repo.get_by_id.return_value = project

        usecase = RemoveMemberUseCase(mock_repo)
        with pytest.raises(BusinessRuleViolationError):
            await usecase.execute(
                project_id=1, user_id=1, requesting_user_id=1
            )


class TestListMembersUseCase:

    async def test_list_members_as_member(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        members = [
            ProjectMember(id=1, project_id=1, user_id=1, role=ProjectRole.LIDER),
            ProjectMember(id=2, project_id=1, user_id=2, role=ProjectRole.INVESTIGADOR),
        ]
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.return_value = members[0]
        mock_repo.list_members.return_value = members

        usecase = ListMembersUseCase(mock_repo)
        result = await usecase.execute(project_id=1, requesting_user_id=1)

        assert len(result) == 2

    async def test_list_members_non_member_raises(self, mock_repo):
        project = Project(id=1, name="Test", owner_id=1)
        mock_repo.get_by_id.return_value = project
        mock_repo.get_member.return_value = None

        usecase = ListMembersUseCase(mock_repo)
        with pytest.raises(PermissionDeniedError):
            await usecase.execute(project_id=1, requesting_user_id=99)


class TestListProjectsUseCase:

    async def test_list_projects(self, mock_repo):
        projects = [
            Project(id=1, name="Project 1", owner_id=1),
            Project(id=2, name="Project 2", owner_id=2),
        ]
        mock_repo.list_by_user.return_value = projects

        usecase = ListProjectsUseCase(mock_repo)
        result = await usecase.execute(user_id=1)

        assert len(result) == 2
        mock_repo.list_by_user.assert_called_once_with(
            user_id=1, skip=0, limit=100
        )
