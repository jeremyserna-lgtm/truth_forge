"""Services module for truth_forge."""

# This __init__.py is crucial for the service auto-registration.
# By importing the service classes here, we ensure that the @register_service()
# decorator is executed, which populates the ServiceFactory's registry.

from truth_forge.services.action import ActionService
from truth_forge.services.base import BaseService, ServiceState
from truth_forge.services.cognition import CognitionService
from truth_forge.services.factory import ServiceFactory, get_service
from truth_forge.services.governance import GovernanceService
from truth_forge.services.knowledge import KnowledgeService
from truth_forge.services.logging import LoggingService
from truth_forge.services.mediator import ServiceMediator
from truth_forge.services.perception import PerceptionService
from truth_forge.services.relationship import RelationshipService
from truth_forge.services.secret import SecretService


__all__ = [
    "ActionService",
    "BaseService",
    "CognitionService",
    "ServiceFactory",
    "get_service",
    "GovernanceService",
    "KnowledgeService",
    "LoggingService",
    "ServiceMediator",
    "PerceptionService",
    "RelationshipService",
    "SecretService",
    "ServiceState",
]
