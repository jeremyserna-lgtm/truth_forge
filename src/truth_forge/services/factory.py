"""Service Factory for dependency injection.

RISK MITIGATION: Fixes circular dependency issues like:
- UniversalResonanceService ↔ CareService
- Service A → Service B → Service A

Uses lazy loading and interface-based injection to break cycles.

Usage:
    from truth_forge.services.factory import get_service, ServiceFactory

    # Get a service by name (lazy loaded)
    knowledge = get_service("knowledge")

    # Register a custom service
    ServiceFactory.register("custom", MyCustomService)

    # Get with dependency injection
    service = ServiceFactory.create("analytics", dependencies={"knowledge": knowledge})
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

import structlog


if TYPE_CHECKING:
    from collections.abc import Callable

    from truth_forge.services.base import BaseService

T = TypeVar("T", bound="BaseService")

logger = structlog.get_logger(__name__)


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered."""

    pass


class CircularDependencyError(Exception):
    """Raised when circular dependency detected."""

    pass


class ServiceFactory:
    """Factory for creating and managing service instances.

    Features:
    - Lazy loading (services created on first access)
    - Singleton pattern (one instance per service)
    - Dependency injection support
    - Circular dependency detection

    Thread-safe via locking.

    Example:
        # Register services
        ServiceFactory.register("knowledge", KnowledgeService)
        ServiceFactory.register("analytics", AnalyticsService)

        # Get service instance (created lazily)
        knowledge = ServiceFactory.get("knowledge")

        # Create with explicit dependencies
        analytics = ServiceFactory.create(
            "analytics",
            dependencies={"knowledge": knowledge}
        )
    """

    _registry: ClassVar[dict[str, type[BaseService]]] = {}
    _instances: ClassVar[dict[str, BaseService]] = {}
    _creating: ClassVar[set[str]] = set()  # For circular dependency detection
    _lock: ClassVar[threading.RLock] = threading.RLock()

    @classmethod
    def register(
        cls,
        name: str,
        service_class: type[BaseService],
        override: bool = False,
    ) -> None:
        """Register a service class.

        Args:
            name: Service name (must match service_class.service_name).
            service_class: Service class to register.
            override: Allow overriding existing registration.

        Raises:
            ValueError: If name already registered and override=False.
        """
        with cls._lock:
            if name in cls._registry and not override:
                raise ValueError(
                    f"Service '{name}' already registered. Use override=True to replace."
                )
            cls._registry[name] = service_class
            logger.debug("service_registered", service=name)

    @classmethod
    def get(cls, name: str) -> BaseService:
        """Get a service instance by name (singleton pattern).

        Creates the instance on first access (lazy loading).

        Args:
            name: Service name.

        Returns:
            Service instance.

        Raises:
            ServiceNotFoundError: If service not registered.
            CircularDependencyError: If circular dependency detected.
        """
        with cls._lock:
            # Return existing instance if available
            if name in cls._instances:
                return cls._instances[name]

            # Check for circular dependency
            if name in cls._creating:
                raise CircularDependencyError(
                    f"Circular dependency detected while creating '{name}'. "
                    f"Creation stack: {cls._creating}"
                )

            # Check if registered
            if name not in cls._registry:
                raise ServiceNotFoundError(
                    f"Service '{name}' not registered. Available: {list(cls._registry.keys())}"
                )

            # Create instance
            cls._creating.add(name)
            try:
                service_class = cls._registry[name]
                instance = service_class()
                cls._instances[name] = instance
                logger.info("service_created", service=name)
                return instance
            finally:
                cls._creating.discard(name)

    @classmethod
    def create(
        cls,
        name: str,
        dependencies: dict[str, BaseService] | None = None,
        **kwargs: Any,
    ) -> BaseService:
        """Create a new service instance with explicit dependencies.

        Unlike get(), this always creates a new instance and allows
        injecting specific dependencies.

        Args:
            name: Service name.
            dependencies: Services to inject (by name).
            **kwargs: Additional constructor arguments.

        Returns:
            New service instance.

        Raises:
            ServiceNotFoundError: If service not registered.
        """
        with cls._lock:
            if name not in cls._registry:
                raise ServiceNotFoundError(
                    f"Service '{name}' not registered. Available: {list(cls._registry.keys())}"
                )

            service_class = cls._registry[name]

            # Create instance
            instance = service_class(**kwargs)

            # Inject dependencies
            if dependencies:
                for dep_name, dep_instance in dependencies.items():
                    setattr(instance, f"_{dep_name}", dep_instance)
                    logger.debug(
                        "dependency_injected",
                        service=name,
                        dependency=dep_name,
                    )

            return instance

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations and instances.

        Primarily for testing.
        """
        with cls._lock:
            # Shutdown all instances (iterate over a copy to avoid dict modification during iteration)
            for name, instance in list(cls._instances.items()):
                try:
                    instance.shutdown()
                except Exception as e:
                    logger.error(
                        "shutdown_failed",
                        service=name,
                        error=str(e),
                    )
            cls._registry.clear()
            cls._instances.clear()
            cls._creating.clear()
            logger.info("factory_cleared")

    @classmethod
    def list_services(cls) -> list[str]:
        """List all registered service names.

        Returns:
            List of service names.
        """
        with cls._lock:
            return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a service is registered.

        Args:
            name: Service name.

        Returns:
            True if registered.
        """
        with cls._lock:
            return name in cls._registry

    @classmethod
    def shutdown_all(cls) -> dict[str, bool]:
        """Shutdown all service instances.

        Returns:
            Dict mapping service names to shutdown success.
        """
        results: dict[str, bool] = {}
        with cls._lock:
            for name, instance in cls._instances.items():
                try:
                    instance.shutdown()
                    results[name] = True
                except Exception as e:
                    logger.error(
                        "shutdown_failed",
                        service=name,
                        error=str(e),
                    )
                    results[name] = False
            cls._instances.clear()
        return results


def get_service(name: str) -> BaseService:
    """Convenience function to get a service instance.

    Args:
        name: Service name.

    Returns:
        Service instance.

    Example:
        >>> knowledge = get_service("knowledge")
        >>> knowledge.inhale({"content": "..."})
    """
    return ServiceFactory.get(name)


def register_service(
    name: str | None = None,
) -> Callable[[type[T]], type[T]]:
    """Decorator to register a service class.

    Args:
        name: Optional service name (defaults to class's service_name).

    Returns:
        Decorator function.

    Example:
        @register_service()
        class KnowledgeService(BaseService):
            service_name = "knowledge"
            ...

        # Or with explicit name
        @register_service("custom_knowledge")
        class MyKnowledgeService(BaseService):
            service_name = "custom_knowledge"
            ...
    """

    def decorator(cls: type[T]) -> type[T]:
        service_name = name or getattr(cls, "service_name", None)
        if not service_name:
            raise ValueError(
                f"Service class {cls.__name__} must define 'service_name' "
                "or pass name to @register_service()"
            )
        ServiceFactory.register(service_name, cls)
        return cls

    return decorator


# =========================================================================
# Auto-registration of core services
# =========================================================================


def _auto_register_services() -> None:
    """Auto-register core services.

    Called at import time to register standard services.
    Services are loaded lazily, so this just registers the classes.

    The @register_service() decorator handles the actual registration,
    so importing the module is sufficient.
    """
    # Import service modules here to trigger registration via @register_service()
    # This is populated as services are migrated
    import contextlib

    # Governance service - organism self-observation (DNA capability)
    with contextlib.suppress(ImportError):
        from truth_forge.services.governance import GovernanceService  # noqa: F401

    # Knowledge service - LLM-powered knowledge extraction
    with contextlib.suppress(ImportError):
        from truth_forge.services.knowledge import KnowledgeService  # noqa: F401


# Register services on import
_auto_register_services()
