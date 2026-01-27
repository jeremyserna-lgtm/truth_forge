"""Session Pattern Detection.

Detects browsing patterns like research sessions, deep dives,
context switches, and computes focus scores.

THE_PATTERN: Visits (HOLD₁) → Pattern Detection (AGENT) → Insights (HOLD₂)
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .extractor import BrowserVisit


@dataclass
class ResearchSession:
    """A detected research session - clustered visits by time and topic."""
    
    session_id: str
    start_time: datetime
    end_time: datetime
    visits: List[BrowserVisit]
    primary_category: Optional[str]
    domains: List[str]
    duration_minutes: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": round(self.duration_minutes, 1),
            "visit_count": len(self.visits),
            "primary_category": self.primary_category,
            "domains": self.domains[:10],  # Top 10
            "domain_count": len(set(self.domains)),
        }


@dataclass
class DeepDive:
    """A deep dive - extended time on single domain."""
    
    domain: str
    category: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    visit_count: int
    urls: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "category": self.category,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": round(self.duration_minutes, 1),
            "visit_count": self.visit_count,
            "sample_urls": self.urls[:5],
        }


@dataclass
class ContextSwitch:
    """A context switch - rapid domain change."""
    
    timestamp: datetime
    from_domain: str
    to_domain: str
    from_category: Optional[str]
    to_category: Optional[str]
    gap_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "from_domain": self.from_domain,
            "to_domain": self.to_domain,
            "from_category": self.from_category,
            "to_category": self.to_category,
            "gap_seconds": round(self.gap_seconds, 1),
        }


@dataclass
class FocusMetrics:
    """Computed focus metrics from browsing patterns."""
    
    focus_score: float  # 0-100
    total_sessions: int
    avg_session_length_minutes: float
    deep_dive_count: int
    context_switch_count: int
    dominant_category: Optional[str]
    time_by_category: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "focus_score": round(self.focus_score, 1),
            "total_sessions": self.total_sessions,
            "avg_session_length_minutes": round(self.avg_session_length_minutes, 1),
            "deep_dive_count": self.deep_dive_count,
            "context_switch_count": self.context_switch_count,
            "dominant_category": self.dominant_category,
            "time_by_category_minutes": {k: round(v, 1) for k, v in self.time_by_category.items()},
        }


class PatternDetector:
    """Detect browsing patterns from visit history."""
    
    # Configuration
    SESSION_GAP_MINUTES = 5  # Gap that splits sessions
    DEEP_DIVE_MIN_MINUTES = 10  # Minimum for deep dive
    CONTEXT_SWITCH_MAX_SECONDS = 30  # Max gap for context switch
    
    def __init__(self, visits: List[BrowserVisit]):
        """Initialize with visits (should be sorted by time, newest first)."""
        # Sort chronologically (oldest first) for pattern detection
        self.visits = sorted(visits, key=lambda v: v.visit_time)
    
    def detect_research_sessions(self) -> List[ResearchSession]:
        """Cluster visits into research sessions.
        
        Sessions are split when gap > SESSION_GAP_MINUTES.
        """
        if not self.visits:
            return []
        
        sessions = []
        current_session: List[BrowserVisit] = [self.visits[0]]
        
        for i in range(1, len(self.visits)):
            prev = self.visits[i - 1]
            curr = self.visits[i]
            
            gap = (curr.visit_time - prev.visit_time).total_seconds() / 60
            
            if gap > self.SESSION_GAP_MINUTES:
                # End current session, start new one
                if current_session:
                    sessions.append(self._build_session(current_session, len(sessions)))
                current_session = [curr]
            else:
                current_session.append(curr)
        
        # Don't forget last session
        if current_session:
            sessions.append(self._build_session(current_session, len(sessions)))
        
        return sessions
    
    def _build_session(self, visits: List[BrowserVisit], index: int) -> ResearchSession:
        """Build a ResearchSession from visits."""
        start = visits[0].visit_time
        end = visits[-1].visit_time
        duration = (end - start).total_seconds() / 60
        
        # Get primary category
        categories = [v.category for v in visits if v.category]
        primary = max(set(categories), key=categories.count) if categories else None
        
        # Get domains
        domains = [v.domain for v in visits]
        
        return ResearchSession(
            session_id=f"session_{index}",
            start_time=start,
            end_time=end,
            visits=visits,
            primary_category=primary,
            domains=domains,
            duration_minutes=duration,
        )
    
    def detect_deep_dives(self) -> List[DeepDive]:
        """Detect extended time on single domains.
        
        A deep dive is 10+ minutes on a single domain.
        """
        if not self.visits:
            return []
        
        deep_dives = []
        
        # Group consecutive visits by domain
        current_domain = self.visits[0].domain
        current_visits: List[BrowserVisit] = [self.visits[0]]
        
        for i in range(1, len(self.visits)):
            curr = self.visits[i]
            
            if curr.domain == current_domain:
                current_visits.append(curr)
            else:
                # Check if current run qualifies as deep dive
                if current_visits:
                    dive = self._check_deep_dive(current_visits)
                    if dive:
                        deep_dives.append(dive)
                
                current_domain = curr.domain
                current_visits = [curr]
        
        # Check last run
        if current_visits:
            dive = self._check_deep_dive(current_visits)
            if dive:
                deep_dives.append(dive)
        
        return deep_dives
    
    def _check_deep_dive(self, visits: List[BrowserVisit]) -> Optional[DeepDive]:
        """Check if visits qualify as a deep dive."""
        if len(visits) < 2:
            return None
        
        start = visits[0].visit_time
        end = visits[-1].visit_time
        duration = (end - start).total_seconds() / 60
        
        if duration < self.DEEP_DIVE_MIN_MINUTES:
            return None
        
        return DeepDive(
            domain=visits[0].domain,
            category=visits[0].category,
            start_time=start,
            end_time=end,
            duration_minutes=duration,
            visit_count=len(visits),
            urls=[v.url for v in visits],
        )
    
    def detect_context_switches(self) -> List[ContextSwitch]:
        """Detect rapid switches between different domains.
        
        Context switches happen when domain changes within 30 seconds.
        """
        if len(self.visits) < 2:
            return []
        
        switches = []
        
        for i in range(1, len(self.visits)):
            prev = self.visits[i - 1]
            curr = self.visits[i]
            
            # Skip if same domain
            if prev.domain == curr.domain:
                continue
            
            gap = (curr.visit_time - prev.visit_time).total_seconds()
            
            # Only count rapid switches
            if gap <= self.CONTEXT_SWITCH_MAX_SECONDS:
                switches.append(ContextSwitch(
                    timestamp=curr.visit_time,
                    from_domain=prev.domain,
                    to_domain=curr.domain,
                    from_category=prev.category,
                    to_category=curr.category,
                    gap_seconds=gap,
                ))
        
        return switches
    
    def get_focus_score(self) -> FocusMetrics:
        """Compute overall focus metrics.
        
        Focus score (0-100) based on:
        - Session length (longer = more focused)
        - Deep dives (more = more focused)
        - Context switches (more = less focused)
        """
        sessions = self.detect_research_sessions()
        deep_dives = self.detect_deep_dives()
        switches = self.detect_context_switches()
        
        # Calculate average session length
        if sessions:
            avg_session = sum(s.duration_minutes for s in sessions) / len(sessions)
        else:
            avg_session = 0
        
        # Calculate time by category
        time_by_category: Dict[str, float] = defaultdict(float)
        for session in sessions:
            if session.primary_category:
                time_by_category[session.primary_category] += session.duration_minutes
        
        # Find dominant category
        dominant = max(time_by_category.items(), key=lambda x: x[1])[0] if time_by_category else None
        
        # Compute focus score
        # Base: 50
        # +10 for each deep dive (max +30)
        # +5 for each 10 minutes avg session (max +20)
        # -5 for each 10 context switches (max -30)
        
        score = 50
        score += min(30, len(deep_dives) * 10)
        score += min(20, (avg_session / 10) * 5)
        score -= min(30, (len(switches) / 10) * 5)
        score = max(0, min(100, score))
        
        return FocusMetrics(
            focus_score=score,
            total_sessions=len(sessions),
            avg_session_length_minutes=avg_session,
            deep_dive_count=len(deep_dives),
            context_switch_count=len(switches),
            dominant_category=dominant,
            time_by_category=dict(time_by_category),
        )
