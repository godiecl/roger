"""
Project role enum for ROGER - Valeria API.
Defines differentiated roles within a project (RF-10).
"""

from enum import Enum


class ProjectRole(str, Enum):
    """Roles within a project for differentiated permissions."""

    LIDER = "lider"
    INVESTIGADOR = "investigador"
    COLABORADOR = "colaborador"
    OBSERVADOR = "observador"

    @classmethod
    def can_manage_members(cls, role: "ProjectRole") -> bool:
        """Check if role can add/remove members."""
        return role == cls.LIDER

    @classmethod
    def can_edit_project(cls, role: "ProjectRole") -> bool:
        """Check if role can edit project details."""
        return role in [cls.LIDER, cls.INVESTIGADOR]

    @classmethod
    def can_share_content(cls, role: "ProjectRole") -> bool:
        """Check if role can share information and content."""
        return role in [cls.LIDER, cls.INVESTIGADOR, cls.COLABORADOR]

    @classmethod
    def can_view_content(cls, role: "ProjectRole") -> bool:
        """Check if role can view project content."""
        return True  # All roles can view
