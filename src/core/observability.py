"""
Observability — Truth Forge Core
Structured logging, metrics collection, and audit trail.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredLogger:
    """
    JSON-structured logger for federation-compatible logging.
    All logs are JSONL format for machine parsing.
    """
    
    def __init__(self, organism: str = "truth_forge", log_dir: str = "logs"):
        self.organism = organism
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "organism.jsonl"
        self.logger = logging.getLogger(f"{organism}.observability")
        
    def log_event(self, event_type: str, data: Dict[str, Any], 
                   level: str = "info") -> Dict[str, Any]:
        """Log a structured event."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "organism": self.organism,
            "role": "THE_BRAIN",
            "event_type": event_type,
            "level": level,
            "data": data
        }
        
        # Write to JSONL file
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write log: {e}")
            
        # Also log via standard logging
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(f"[{event_type}] {json.dumps(data)}")
        
        return record
    
    def log_cycle(self, cycle_num: int, signals: Dict, actions: int):
        """Log a heartbeat cycle."""
        return self.log_event("heartbeat_cycle", {
            "cycle": cycle_num,
            "signals": signals,
            "actions_taken": actions
        })
    
    def log_federation(self, event: str, peer: str, data: Dict):
        """Log a federation event."""
        return self.log_event("federation", {
            "event": event,
            "peer": peer,
            **data
        })
