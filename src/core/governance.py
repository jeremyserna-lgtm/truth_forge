"""
Governance — Truth Forge Core
Enforces domain boundaries, cost limits, and authority levels.
Prevents identity drift: Forge must remain THE BRAIN.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml  # type: ignore[import-not-found]
import logging
from datetime import datetime, timezone


class GovernanceEnforcer:
    """
    Enforces governance rules defined in config/governance.yaml.
    
    Primary responsibilities:
    - Validate actions against domain boundaries
    - Enforce cost limits  
    - Prevent identity drift
    - Log governance events
    """
    
    def __init__(self, governance_path: str = "config/governance.yaml"):
        self.logger = logging.getLogger("truth_forge.governance")
        self.config = self._load_governance(governance_path)
        self.violations: List[Dict] = []
        
    def _load_governance(self, path: str) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            self.logger.warning(f"Governance config not found: {path}")
            return {}
        try:
            return yaml.safe_load(p.read_text()) or {}
        except Exception as e:
            self.logger.error(f"Failed to load governance: {e}")
            return {}
    
    def check_action(self, action: str) -> bool:
        """Check if an action is within governance boundaries."""
        never_do = self.config.get("boundaries", {}).get("never_do", [])
        
        if action in never_do:
            self._record_violation(action, "BOUNDARY_VIOLATION", 
                f"Action '{action}' is outside this organism's domain")
            return False
            
        requires_approval = self.config.get("authority", {}).get("requires_approval", [])
        if action in requires_approval:
            self.logger.warning(f"Action '{action}' requires Genesis approval")
            return False  # In future: request approval from Genesis
            
        return True
    
    def check_cost(self, cost: float, period: str = "cycle") -> bool:
        """Check if a cost is within governance limits."""
        limits = self.config.get("cost_limits", {})
        
        if period == "cycle":
            max_cost = limits.get("max_llm_cost_per_cycle", float('inf'))
        elif period == "daily":
            max_cost = limits.get("max_daily_llm_spend", float('inf'))
        else:
            max_cost = float('inf')
            
        if cost > max_cost:
            self._record_violation(
                f"cost_{period}", "COST_VIOLATION",
                f"Cost ${cost:.2f} exceeds {period} limit ${max_cost:.2f}")
            return False
            
        threshold = limits.get("alert_threshold", 0.80)
        if cost > max_cost * threshold:
            self.logger.warning(
                f"Cost ${cost:.2f} is at {cost/max_cost*100:.0f}% of {period} limit")
            
        return True
    
    def _record_violation(self, action: str, violation_type: str, message: str):
        violation = {
            "action": action,
            "type": violation_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "organism": "truth_forge",
            "role": "THE_BRAIN"
        }
        self.violations.append(violation)
        self.logger.error(f"GOVERNANCE VIOLATION: {message}")
    
    def get_violations(self) -> List[Dict]:
        return self.violations.copy()
    
    def is_compliant(self) -> bool:
        return len(self.violations) == 0
