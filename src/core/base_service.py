"""
Base Service — Truth Forge Core
Provides the foundational service class that all Truth Forge services extend.
Implements HOLD → AGENT → HOLD pattern at the service level.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging
import json
from pathlib import Path


class BaseService(ABC):
    """
    Abstract base for all Truth Forge services.
    
    Every service follows the HOLD → AGENT → HOLD pattern:
    - HOLD IN: Receive input, validate, prepare
    - AGENT: Process according to service logic  
    - HOLD OUT: Validate output, emit result
    """
    
    SERVICE_NAME: str = "unnamed"
    SERVICE_VERSION: str = "0.1.0"
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(f"truth_forge.{self.SERVICE_NAME}")
        self.config = self._load_config(config_path) if config_path else {}
        self.started_at = datetime.now(timezone.utc)
        self._healthy = True
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load service configuration from YAML or JSON."""
        p = Path(path)
        if not p.exists():
            self.logger.warning(f"Config not found: {path}")
            return {}
        try:
            if p.suffix in ('.yaml', '.yml'):
                import yaml  # type: ignore[import-not-found]
                return yaml.safe_load(p.read_text()) or {}
            elif p.suffix == '.json':
                return json.loads(p.read_text())
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}
    
    def hold_in(self, input_data: Any) -> Any:
        """
        HOLD IN: Receive and validate input.
        Override to add input validation.
        """
        self.logger.debug(f"HOLD IN: Receiving input")
        return input_data
    
    @abstractmethod
    def agent(self, validated_input: Any) -> Any:
        """
        AGENT: Core processing logic.
        Subclasses MUST implement this.
        """
        ...
    
    def hold_out(self, result: Any) -> Any:
        """
        HOLD OUT: Validate and emit output.
        Override to add output validation.
        """
        self.logger.debug(f"HOLD OUT: Emitting result")
        return result
    
    def process(self, input_data: Any) -> Any:
        """Execute the full HOLD → AGENT → HOLD cycle."""
        validated = self.hold_in(input_data)
        result = self.agent(validated)
        output = self.hold_out(result)
        return output
    
    @property
    def is_healthy(self) -> bool:
        return self._healthy
    
    def health_check(self) -> Dict[str, Any]:
        """Return service health status."""
        return {
            "service": self.SERVICE_NAME,
            "version": self.SERVICE_VERSION,
            "healthy": self.is_healthy,
            "uptime_seconds": (datetime.now(timezone.utc) - self.started_at).total_seconds(),
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    
    def manifest(self) -> Dict[str, Any]:
        """Return service manifest for federation registration."""
        return {
            "name": self.SERVICE_NAME,
            "version": self.SERVICE_VERSION,
            "organism": "truth_forge",
            "role": "THE_BRAIN",
            "pattern": "HOLD_AGENT_HOLD"
        }
