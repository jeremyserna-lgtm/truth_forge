"""
Test the initialization of all services to detect circular dependencies and other import errors.
"""
import importlib
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from truth_forge.services.factory import ServiceFactory


@pytest.fixture
def temp_services_dir(tmp_path: Path) -> Path:
    """Create temporary services directory structure."""
    services_dir = tmp_path / "services"
    services_dir.mkdir(parents=True)
    return services_dir


# Map service names to their classes for direct instantiation testing
# Order matters: services are registered in dependency order
SERVICE_CLASSES: dict[str, tuple[str, str]] = {
    "secret": ("truth_forge.services.secret.service", "SecretService"),
    "mediator": ("truth_forge.services.mediator.service", "ServiceMediator"),
    "governance": ("truth_forge.services.governance.service", "GovernanceService"),
    "knowledge": ("truth_forge.services.knowledge.service", "KnowledgeService"),
    "logging": ("truth_forge.services.logging.service", "LoggingService"),
    "perception": ("truth_forge.services.perception.service", "PerceptionService"),
    "relationship": ("truth_forge.services.relationship.service", "RelationshipService"),
    "action": ("truth_forge.services.action.service", "ActionService"),
    "cognition": ("truth_forge.services.cognition.service", "CognitionService"),
}


@pytest.fixture
def register_all_services(temp_services_dir: Path) -> Any:
    """Register all services before tests run."""
    with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
        # Register all services in dependency order
        for service_name, (module_path, class_name) in SERVICE_CLASSES.items():
            module = importlib.import_module(module_path)
            service_class = getattr(module, class_name)
            if not ServiceFactory.is_registered(service_name):
                ServiceFactory.register(service_name, service_class)

        yield

        ServiceFactory.clear()


@pytest.mark.parametrize("service_name", list(SERVICE_CLASSES.keys()))
def test_service_initialization(
    service_name: str, temp_services_dir: Path, register_all_services: Any
) -> None:
    """
    Tests that a service can be instantiated without raising an import or dependency error.
    This is not a functional test, but a crucial test for architectural integrity.
    """
    module_path, class_name = SERVICE_CLASSES[service_name]

    with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
        try:
            # Import the module and get the class
            module = importlib.import_module(module_path)
            service_class = getattr(module, class_name)

            # Instantiate the service
            service = service_class()

            assert service is not None, f"Service '{service_name}' should not be None"
            assert service.service_name == service_name, "Service name should match"
        except Exception as e:
            pytest.fail(f"Failed to initialize service '{service_name}': {e}")
