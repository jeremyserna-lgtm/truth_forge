"""Time utilities for browser history tools.

Provides consistent time-bounding across all tools.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


# Named periods for convenience
NAMED_PERIODS = {
    "today": lambda: (datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0), None),
    "yesterday": lambda: (
        datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
        datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    ),
    "this_week": lambda: (datetime.now(timezone.utc) - timedelta(days=7), None),
    "this_month": lambda: (datetime.now(timezone.utc) - timedelta(days=30), None),
    "last_hour": lambda: (datetime.now(timezone.utc) - timedelta(hours=1), None),
}


def period_help() -> str:
    """Return help text for named periods."""
    return f"Options: {', '.join(NAMED_PERIODS.keys())}"


def resolve_time_window(
    period: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    minutes: Optional[int] = None,
    hours: Optional[int] = None,
    days: Optional[int] = None,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Resolve time window from various parameters.
    
    Priority:
    1. Named period (today, yesterday, etc.)
    2. Explicit since/until
    3. Relative (minutes, hours, days)
    4. Default: last 24 hours
    
    Returns:
        Tuple of (since_datetime, until_datetime)
    """
    now = datetime.now(timezone.utc)
    
    # Named period takes priority
    if period and period in NAMED_PERIODS:
        return NAMED_PERIODS[period]()
    
    # Explicit since/until
    since_dt = None
    until_dt = None
    
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            pass
    
    if until:
        try:
            until_dt = datetime.fromisoformat(until.replace("Z", "+00:00"))
        except ValueError:
            pass
    
    if since_dt or until_dt:
        return since_dt, until_dt
    
    # Relative time
    if minutes:
        return now - timedelta(minutes=minutes), None
    
    if hours:
        return now - timedelta(hours=hours), None
    
    if days:
        return now - timedelta(days=days), None
    
    # Default: last 24 hours
    return now - timedelta(hours=24), None
