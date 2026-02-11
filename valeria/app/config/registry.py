"""
Dependency Injection Registry for ROGER - Valeria API
Manages dependencies and their lifecycle
"""

from typing import Dict, Any, Type, TypeVar, Optional
from functools import lru_cache

T = TypeVar('T')


class DependencyRegistry:
    """
    Simple dependency injection container.
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, interface: Type[T], implementation: Any) -> None:
        """
        Register a service implementation for an interface.
        
        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation
        """
        self._services[interface] = implementation
    
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """
        Register a singleton instance.
        
        Args:
            interface: The interface/abstract class
            instance: The singleton instance
        """
        self._singletons[interface] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance.
        
        Args:
            interface: The interface to resolve
            
        Returns:
            The service instance
            
        Raises:
            KeyError: If service not registered
        """
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check registered services
        if interface in self._services:
            implementation = self._services[interface]
            if callable(implementation):
                return implementation()
            return implementation
        
        raise KeyError(f"Service not registered: {interface}")
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._singletons.clear()


# Global registry instance
@lru_cache()
def get_registry() -> DependencyRegistry:
    """Get the global dependency registry."""
    return DependencyRegistry()
