"""
Base classes for ANIMA memory graphs.

All graphs inherit from BaseGraph for consistent interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

import structlog


logger = structlog.get_logger(__name__)


@dataclass
class BaseNode:
    """Base class for all graph nodes."""

    node_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    significance: float = 0.5  # 0-1, used for decay calculations

    def touch(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed = datetime.utcnow()


NodeT = TypeVar("NodeT", bound=BaseNode)


class BaseGraph(ABC, Generic[NodeT]):
    """
    Abstract base class for all ANIMA memory graphs.

    Provides consistent interface for:
    - Ingestion (adding content to graph)
    - Querying (retrieving relevant content)
    - Decay (intelligent forgetting)
    - Persistence (storage and retrieval)
    """

    def __init__(self, storage_path: str) -> None:
        """
        Initialize the graph.

        Args:
            storage_path: Directory for graph storage.
        """
        self._storage_path = storage_path
        self._decay_rate = 0.01

    @abstractmethod
    async def ingest(self, content: str, **kwargs: Any) -> list[NodeT]:
        """
        Ingest content into the graph.

        Args:
            content: The content to ingest.
            **kwargs: Graph-specific parameters.

        Returns:
            List of created nodes.
        """
        pass

    @abstractmethod
    async def query(self, query: str, k: int = 10, **kwargs: Any) -> list[NodeT]:
        """
        Query the graph for relevant nodes.

        Args:
            query: The query string.
            k: Maximum number of results.
            **kwargs: Graph-specific parameters.

        Returns:
            List of relevant nodes.
        """
        pass

    @abstractmethod
    async def get(self, node_id: str) -> NodeT | None:
        """
        Get a specific node by ID.

        Args:
            node_id: The node identifier.

        Returns:
            The node if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[NodeT]:
        """
        Get all nodes in the graph.

        Returns:
            All nodes.
        """
        pass

    @abstractmethod
    async def update(self, node: NodeT) -> None:
        """
        Update an existing node.

        Args:
            node: The node to update.
        """
        pass

    @abstractmethod
    async def delete(self, node_id: str) -> None:
        """
        Delete a node from the graph.

        Args:
            node_id: The node identifier.
        """
        pass

    @abstractmethod
    async def archive(self, node: NodeT) -> None:
        """
        Archive a node (move to cold storage).

        Args:
            node: The node to archive.
        """
        pass

    async def decay(self) -> int:
        """
        Run decay cycle on all nodes.

        Returns:
            Number of nodes archived.
        """
        archived_count = 0
        nodes = await self.get_all()

        for node in nodes:
            days_since_access = (datetime.utcnow() - node.last_accessed).days

            if days_since_access > 7:
                # Decay based on access recency and current significance
                decay_factor = self._decay_rate * (1 + days_since_access / 30)
                node.significance *= 1 - decay_factor

                if node.significance < 0.1:
                    await self.archive(node)
                    archived_count += 1
                    logger.info(
                        "node_archived",
                        extra={
                            "node_id": node.node_id,
                            "final_significance": node.significance,
                        },
                    )
                else:
                    await self.update(node)

        return archived_count

    @staticmethod
    def generate_id() -> str:
        """Generate a unique node ID."""
        return str(uuid4())
