"""
Domain exceptions for ROGER - Valeria API
"""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: any):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class ValidationError(DomainException):
    """Raised when domain validation fails."""
    pass


class UnauthorizedError(DomainException):
    """Raised when user is not authorized."""
    pass


class PermissionDeniedError(DomainException):
    """Raised when user doesn't have permission."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass
