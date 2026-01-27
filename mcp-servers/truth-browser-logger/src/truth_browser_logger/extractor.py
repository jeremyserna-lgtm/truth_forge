"""Browser History Extractor - Chrome and Safari support.

Extracts browser history from local SQLite databases with temp-copy
pattern to avoid database locking issues.

THE_PATTERN: Browser DB (HOLD₁) → Temp Copy → Query → Results (HOLD₂)
"""
from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from urllib.parse import urlparse

from .categories import get_category_for_domain
from .consent import check_consent, get_excluded_domains

logger = logging.getLogger(__name__)

# Timestamp conversion constants
# Chrome: microseconds since 1601-01-01
CHROME_EPOCH = 11644473600
# Safari: seconds since 2001-01-01
SAFARI_EPOCH = 978307200


@dataclass
class BrowserVisit:
    """A single browser visit entry."""
    url: str
    title: str
    visit_time: datetime
    domain: str
    category: Optional[str]
    visit_count: int
    browser: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "visit_time": self.visit_time.isoformat(),
            "domain": self.domain,
            "category": self.category,
            "visit_count": self.visit_count,
            "browser": self.browser,
        }


def _chrome_timestamp_to_datetime(chrome_timestamp: int) -> datetime:
    """Convert Chrome timestamp (microseconds since 1601) to datetime."""
    try:
        unix_timestamp = (chrome_timestamp / 1_000_000) - CHROME_EPOCH
        return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    except (OSError, ValueError):
        return datetime.now(timezone.utc)


def _safari_timestamp_to_datetime(safari_timestamp: float) -> datetime:
    """Convert Safari timestamp (seconds since 2001) to datetime."""
    try:
        unix_timestamp = safari_timestamp + SAFARI_EPOCH
        return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    except (OSError, ValueError):
        return datetime.now(timezone.utc)


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def _copy_database_to_temp(db_path: Path) -> Optional[Path]:
    """Copy database to temp location to avoid locking issues.
    
    Browsers lock their history databases. We copy to temp first.
    """
    if not db_path.exists():
        return None
    
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix="browser_history_"))
        temp_path = temp_dir / "history_copy.db"
        shutil.copy2(db_path, temp_path)
        return temp_path
    except Exception as e:
        logger.error(f"Failed to copy database {db_path}: {e}")
        return None


def _cleanup_temp_db(temp_path: Path) -> None:
    """Clean up temporary database copy."""
    try:
        if temp_path and temp_path.exists():
            temp_path.unlink()
            temp_path.parent.rmdir()
    except Exception as e:
        logger.warning(f"Failed to cleanup temp db: {e}")


class BrowserHistoryExtractor:
    """Extract browser history from Chrome and Safari."""
    
    # Database paths (relative to home directory)
    CHROME_PATH = Path("Library/Application Support/Google/Chrome/Default/History")
    SAFARI_PATH = Path("Library/Safari/History.db")
    
    def __init__(self, home_dir: Optional[Path] = None):
        self.home = home_dir or Path.home()
        self._excluded_domains: Optional[set] = None
    
    @property
    def excluded_domains(self) -> set:
        """Get set of excluded domains (cached)."""
        if self._excluded_domains is None:
            self._excluded_domains = set(get_excluded_domains())
        return self._excluded_domains
    
    def _is_excluded(self, domain: str) -> bool:
        """Check if domain should be excluded."""
        if not domain:
            return True
        # Check exact match and parent domains
        parts = domain.split(".")
        for i in range(len(parts)):
            check_domain = ".".join(parts[i:])
            if check_domain in self.excluded_domains:
                return True
        return False
    
    def get_chrome_history(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
        domain_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> List[BrowserVisit]:
        """Extract Chrome browser history."""
        db_path = self.home / self.CHROME_PATH
        
        if not db_path.exists():
            logger.info("Chrome history database not found")
            return []
        
        temp_path = _copy_database_to_temp(db_path)
        if not temp_path:
            return []
        
        visits = []
        try:
            conn = sqlite3.connect(str(temp_path))
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT 
                    urls.url,
                    urls.title,
                    urls.visit_count,
                    visits.visit_time
                FROM urls
                LEFT JOIN visits ON urls.id = visits.url
                WHERE urls.url IS NOT NULL
            """
            params = []
            
            if since:
                chrome_since = int((since.timestamp() + CHROME_EPOCH) * 1_000_000)
                query += " AND visits.visit_time >= ?"
                params.append(chrome_since)
            
            if until:
                chrome_until = int((until.timestamp() + CHROME_EPOCH) * 1_000_000)
                query += " AND visits.visit_time <= ?"
                params.append(chrome_until)
            
            query += " ORDER BY visits.visit_time DESC LIMIT ?"
            params.append(limit * 2)  # Get extra to account for filtering
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                url, title, visit_count, visit_time = row
                
                if not url or not visit_time:
                    continue
                
                domain = _extract_domain(url)
                
                # Skip excluded domains
                if self._is_excluded(domain):
                    continue
                
                # Apply domain filter
                if domain_filter and domain_filter.lower() not in domain.lower():
                    continue
                
                category = get_category_for_domain(domain)
                
                # Apply category filter
                if category_filter and category != category_filter:
                    continue
                
                visit = BrowserVisit(
                    url=url,
                    title=title or "",
                    visit_time=_chrome_timestamp_to_datetime(visit_time),
                    domain=domain,
                    category=category,
                    visit_count=visit_count or 1,
                    browser="chrome",
                )
                visits.append(visit)
                
                if len(visits) >= limit:
                    break
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to extract Chrome history: {e}")
        finally:
            _cleanup_temp_db(temp_path)
        
        return visits
    
    def get_safari_history(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
        domain_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> List[BrowserVisit]:
        """Extract Safari browser history.
        
        NOTE: Requires Full Disk Access permission.
        System Preferences → Security & Privacy → Privacy → Full Disk Access
        """
        db_path = self.home / self.SAFARI_PATH
        
        if not db_path.exists():
            logger.info("Safari history database not found")
            return []
        
        temp_path = _copy_database_to_temp(db_path)
        if not temp_path:
            logger.error(
                "Failed to copy Safari history. This may require Full Disk Access. "
                "Go to System Preferences → Security & Privacy → Privacy → Full Disk Access "
                "and add your terminal or IDE."
            )
            return []
        
        visits = []
        try:
            conn = sqlite3.connect(str(temp_path))
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT 
                    history_items.url,
                    history_items.visit_count,
                    history_visits.visit_time,
                    history_visits.title
                FROM history_items
                LEFT JOIN history_visits ON history_items.id = history_visits.history_item
                WHERE history_items.url IS NOT NULL
            """
            params = []
            
            if since:
                safari_since = since.timestamp() - SAFARI_EPOCH
                query += " AND history_visits.visit_time >= ?"
                params.append(safari_since)
            
            if until:
                safari_until = until.timestamp() - SAFARI_EPOCH
                query += " AND history_visits.visit_time <= ?"
                params.append(safari_until)
            
            query += " ORDER BY history_visits.visit_time DESC LIMIT ?"
            params.append(limit * 2)
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                url, visit_count, visit_time, title = row
                
                if not url or visit_time is None:
                    continue
                
                domain = _extract_domain(url)
                
                if self._is_excluded(domain):
                    continue
                
                if domain_filter and domain_filter.lower() not in domain.lower():
                    continue
                
                category = get_category_for_domain(domain)
                
                if category_filter and category != category_filter:
                    continue
                
                visit = BrowserVisit(
                    url=url,
                    title=title or "",
                    visit_time=_safari_timestamp_to_datetime(visit_time),
                    domain=domain,
                    category=category,
                    visit_count=visit_count or 1,
                    browser="safari",
                )
                visits.append(visit)
                
                if len(visits) >= limit:
                    break
            
            conn.close()
            
        except sqlite3.OperationalError as e:
            if "unable to open" in str(e).lower() or "locked" in str(e).lower():
                logger.error(
                    "Cannot access Safari history. Requires Full Disk Access. "
                    "System Preferences → Security & Privacy → Privacy → Full Disk Access"
                )
            else:
                logger.error(f"SQLite error extracting Safari history: {e}")
        except Exception as e:
            logger.error(f"Failed to extract Safari history: {e}")
        finally:
            _cleanup_temp_db(temp_path)
        
        return visits
    
    def get_all_history(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
        browser: Optional[str] = None,
        domain_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> List[BrowserVisit]:
        """Get history from all browsers (or specific browser)."""
        visits = []
        
        if browser is None or browser.lower() == "chrome":
            visits.extend(self.get_chrome_history(
                since=since,
                until=until,
                limit=limit,
                domain_filter=domain_filter,
                category_filter=category_filter,
            ))
        
        if browser is None or browser.lower() == "safari":
            visits.extend(self.get_safari_history(
                since=since,
                until=until,
                limit=limit,
                domain_filter=domain_filter,
                category_filter=category_filter,
            ))
        
        # Sort by visit time, newest first
        visits.sort(key=lambda v: v.visit_time, reverse=True)
        
        return visits[:limit]
    
    def get_available_browsers(self) -> Dict[str, bool]:
        """Check which browsers have accessible history."""
        return {
            "chrome": (self.home / self.CHROME_PATH).exists(),
            "safari": (self.home / self.SAFARI_PATH).exists(),
        }


# Singleton instance
_extractor: Optional[BrowserHistoryExtractor] = None


def get_extractor() -> BrowserHistoryExtractor:
    """Get singleton extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = BrowserHistoryExtractor()
    return _extractor
