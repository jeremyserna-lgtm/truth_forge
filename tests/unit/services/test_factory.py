"""Unit tests for service factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.base import BaseService
from truth_forge.services.factory import (
    CircularDependencyError,
    ServiceFactory,
    ServiceNotFoundError,
    get_service,
    register_service,
)


@pytest.fixture
def mock_mediator() -> MagicMock:
    """Mock mediator service for tests that use shutdown."""
    mediator = MagicMock()
    mediator.service_name = "mediator"
    mediator.publish = MagicMock()
    return mediator


@pytest.fixture(autouse=True)
def clean_factory() -> Any:
    """Clean factory before and after each test."""
    ServiceFactory.clear()
    yield
    ServiceFactory.clear()


@pytest.fixture
def temp_services_dir(tmp_path: Path) -> Path:
    """Create temporary services directory structure.

    Patches SERVICES_ROOT directly since it's computed at import time.
    """
    services_dir = tmp_path / "services"
    services_dir.mkdir(parents=True)
    return services_dir


class ServiceA(BaseService):
    """Test service A."""

    service_name = "test_a"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        return record


class ServiceB(BaseService):
    """Test service B."""

    service_name = "test_b"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        return record


class TestServiceFactoryRegister:
    """Tests for ServiceFactory.register()."""

    def test_register_service(self) -> None:
        """Test registering a service."""
        ServiceFactory.register("test_a", ServiceA)

        assert ServiceFactory.is_registered("test_a")

    def test_register_duplicate_raises(self) -> None:
        """Test registering duplicate name raises."""
        ServiceFactory.register("test_a", ServiceA)

        with pytest.raises(ValueError, match="already registered"):
            ServiceFactory.register("test_a", ServiceB)

    def test_register_with_override(self) -> None:
        """Test override allows replacing registration."""
        ServiceFactory.register("test_a", ServiceA)
        ServiceFactory.register("test_a", ServiceB, override=True)

        assert ServiceFactory.is_registered("test_a")


class TestServiceFactoryGet:
    """Tests for ServiceFactory.get()."""

    def test_get_unregistered_raises(self) -> None:
        """Test getting unregistered service raises."""
        with pytest.raises(ServiceNotFoundError, match="not registered"):
            ServiceFactory.get("nonexistent")

    def test_get_creates_instance(self, temp_services_dir: Path) -> None:
        """Test get creates service instance."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            ServiceFactory.register("test_a", ServiceA)

            service = ServiceFactory.get("test_a")

            assert isinstance(service, ServiceA)
            assert service.service_name == "test_a"

    def test_get_returns_singleton(self, temp_services_dir: Path) -> None:
        """Test get returns same instance (singleton)."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            ServiceFactory.register("test_a", ServiceA)

            service1 = ServiceFactory.get("test_a")
            service2 = ServiceFactory.get("test_a")

            assert service1 is service2


class TestServiceFactoryCreate:
    """Tests for ServiceFactory.create()."""

    def test_create_unregistered_raises(self) -> None:
        """Test creating unregistered service raises."""
        with pytest.raises(ServiceNotFoundError, match="not registered"):
            ServiceFactory.create("nonexistent")

    def test_create_new_instance(self, temp_services_dir: Path) -> None:
        """Test create always makes new instance."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            ServiceFactory.register("test_a", ServiceA)

            service1 = ServiceFactory.create("test_a")
            service2 = ServiceFactory.create("test_a")

            assert service1 is not service2

    def test_create_with_dependencies(self, temp_services_dir: Path) -> None:
        """Test create injects dependencies."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            ServiceFactory.register("test_a", ServiceA)
            ServiceFactory.register("test_b", ServiceB)

            dep_service = ServiceFactory.get("test_a")
            service = ServiceFactory.create("test_b", dependencies={"test_a": dep_service})

            assert hasattr(service, "_test_a")
            assert service._test_a is dep_service


class TestServiceFactoryUtilities:
    """Tests for ServiceFactory utility methods."""

    def test_list_services(self) -> None:
        """Test listing registered services."""
        ServiceFactory.register("test_a", ServiceA)
        ServiceFactory.register("test_b", ServiceB)

        services = ServiceFactory.list_services()

        assert "test_a" in services
        assert "test_b" in services

    def test_is_registered_true(self) -> None:
        """Test is_registered returns True."""
        ServiceFactory.register("test_a", ServiceA)

        assert ServiceFactory.is_registered("test_a") is True

    def test_is_registered_false(self) -> None:
        """Test is_registered returns False."""
        assert ServiceFactory.is_registered("nonexistent") is False

    def test_clear(self, temp_services_dir: Path) -> None:
        """Test clear removes all registrations."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            ServiceFactory.register("test_a", ServiceA)
            ServiceFactory.get("test_a")  # Create instance

            ServiceFactory.clear()

            assert not ServiceFactory.is_registered("test_a")
            assert ServiceFactory.list_services() == []


class TestServiceFactoryShutdown:
    """Tests for ServiceFactory shutdown."""

    def test_shutdown_all(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test shutdown_all shuts down all instances."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            ServiceFactory.register("test_a", ServiceA)
            ServiceFactory.register("test_b", ServiceB)

            ServiceFactory.get("test_a")
            ServiceFactory.get("test_b")

            results = ServiceFactory.shutdown_all()

            assert results["test_a"] is True
            assert results["test_b"] is True


class TestGetServiceFunction:
    """Tests for get_service convenience function."""

    def test_get_service(self, temp_services_dir: Path) -> None:
        """Test get_service function."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            ServiceFactory.register("test_a", ServiceA)

            service = get_service("test_a")

            assert isinstance(service, ServiceA)


class TestRegisterServiceDecorator:
    """Tests for register_service decorator."""

    def test_decorator_registers(self) -> None:
        """Test decorator registers service."""

        @register_service()
        class DecoratedService(BaseService):
            service_name = "decorated"

            def process(self, record: dict[str, Any]) -> dict[str, Any]:
                return record

        assert ServiceFactory.is_registered("decorated")

    def test_decorator_with_name(self) -> None:
        """Test decorator with explicit name."""

        @register_service("custom_name")
        class CustomService(BaseService):
            service_name = "custom_name"

            def process(self, record: dict[str, Any]) -> dict[str, Any]:
                return record

        assert ServiceFactory.is_registered("custom_name")

    def test_decorator_no_name_raises(self) -> None:
        """Test decorator without service_name raises."""
        with pytest.raises(ValueError, match="must define 'service_name'"):

            @register_service()
            class NoNameService(BaseService):
                def process(self, record: dict[str, Any]) -> dict[str, Any]:
                    return record
