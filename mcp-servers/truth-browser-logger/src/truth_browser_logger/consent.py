"""Consent management for browser history extraction.

Implements consent-based access control following privacy-first principles.
No extraction occurs without explicit consent.

Config files:
- config/browser_history_consent.json - Main consent toggle
- config/browser_history_excluded_domains.json - Domains to never extract
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Config paths
_repo_root = Path(__file__).parent.parent.parent.parent.parent
CONFIG_DIR = _repo_root / "config"
CONSENT_FILE = CONFIG_DIR / "browser_history_consent.json"
EXCLUDED_DOMAINS_FILE = CONFIG_DIR / "browser_history_excluded_domains.json"


def _load_json_config(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    """Load JSON config file with fallback to default."""
    if not path.exists():
        return default
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {path}: {e}")
        return default


def check_consent() -> Tuple[bool, str]:
    """Check if browser history extraction is consented.
    
    Returns:
        Tuple of (allowed, reason)
    """
    default = {
        "consent": False,
        "date": None,
        "notes": "Consent not configured"
    }
    
    config = _load_json_config(CONSENT_FILE, default)
    
    consent = config.get("consent", False)
    
    if not consent:
        reason = (
            "Browser history extraction requires consent. "
            f"Set 'consent': true in {CONSENT_FILE} to enable."
        )
        return False, reason
    
    consent_date = config.get("date")
    if consent_date:
        reason = f"Consent granted on {consent_date}"
    else:
        reason = "Consent granted (no date recorded)"
    
    return True, reason


def get_excluded_domains() -> List[str]:
    """Get list of domains to exclude from extraction.
    
    These are domains that should never appear in extracted history,
    such as banking, healthcare, or other sensitive sites.
    """
    default = {
        "excluded_domains": [],
        "notes": "Add sensitive domains to exclude"
    }
    
    config = _load_json_config(EXCLUDED_DOMAINS_FILE, default)
    
    return config.get("excluded_domains", [])


def get_consent_status() -> Dict[str, Any]:
    """Get full consent status for reporting."""
    allowed, reason = check_consent()
    excluded = get_excluded_domains()
    
    return {
        "consent": allowed,
        "reason": reason,
        "excluded_domain_count": len(excluded),
        "consent_file": str(CONSENT_FILE),
        "excluded_domains_file": str(EXCLUDED_DOMAINS_FILE),
    }


def ensure_consent_or_raise() -> None:
    """Ensure consent is granted, raise if not."""
    allowed, reason = check_consent()
    if not allowed:
        raise PermissionError(reason)
