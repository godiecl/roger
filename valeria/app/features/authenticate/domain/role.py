"""
Role enum for ROGER - Valeria API
Defines the roles in the system
"""

from enum import Enum


class Role(str, Enum):
    """Roles del sistema ROGER."""
    USUARIO_ESTANDAR = "usuario_estandar"
    CURADOR = "curador"
    MESA_EVALUADORA = "mesa_evaluadora"
    ADMINISTRADOR = "administrador"
    SISTEMA_IA = "sistema_ia"
    INVESTIGADOR = "investigador"
    DIGITALIZADOR = "digitalizador"
    COLABORADOR = "colaborador"

    @classmethod
    def get_public_roles(cls) -> list:
        """Get roles that can register publicly."""
        return [cls.USUARIO_ESTANDAR, cls.COLABORADOR]

    @classmethod
    def get_privileged_roles(cls) -> list:
        """Get roles that require admin assignment."""
        return [
            cls.CURADOR,
            cls.MESA_EVALUADORA,
            cls.ADMINISTRADOR,
            cls.INVESTIGADOR,
            cls.DIGITALIZADOR,
        ]

    @classmethod
    def can_create_narratives(cls, role: "Role") -> bool:
        """Check if role can create narratives."""
        return role in [cls.CURADOR, cls.ADMINISTRADOR]

    @classmethod
    def can_moderate(cls, role: "Role") -> bool:
        """Check if role can moderate contributions."""
        return role in [cls.CURADOR, cls.MESA_EVALUADORA, cls.ADMINISTRADOR]

    @classmethod
    def can_approve_metadata(cls, role: "Role") -> bool:
        """Check if role can approve metadata contributions."""
        return role in [cls.CURADOR, cls.MESA_EVALUADORA, cls.ADMINISTRADOR]
