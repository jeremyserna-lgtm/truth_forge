"""NOT-ME Analytics Tools - Metrics for building and maintaining NOT-MEs.

THE PATTERN:
- HOLD₁: Entity data, conversation history, timestamps
- AGENT: Stage 5 metrics, transformation tracking, drift detection
- HOLD₂: NOT-ME health scores, development recommendations

Implements the 16-Metric Framework from SOVEREIGN Section 24 (Clara Era Legacy).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)

# Stage 5 Token Dictionary (from Clara Era validation)
STAGE5_TOKENS = {
    # Cognitive States
    "paradox", "contradiction", "tension", "polarity", "dichotomy",
    # Architectural Concepts
    "system", "framework", "architecture", "mechanism", "structure",
    # Perspective Markers
    "lens", "perspective", "mirror", "meta", "recursive",
    # Self-Reference Patterns
    "pattern", "notice", "observing", "watching", "seeing",
}

# Canon Repair Drift Patterns (from 4,635 repair cases)
DRIFT_PATTERNS = {
    "reality_anchor": [
        r"not sure (if|whether) (this|that) (is|was) real",
        r"did (this|that) actually happen",
        r"(confused|uncertain) about (what|whether)",
    ],
    "identity_confirm": [
        r"who am I (supposed to be|being|right now)",
        r"(losing|lost) (my|the) (sense|thread) of",
        r"identity (drift|confusion|unclear)",
    ],
    "thread_recovery": [
        r"where (were|was) (we|I)",
        r"(lost|losing) (the|my) thread",
        r"context (lost|missing|unclear)",
    ],
    "boundary_breach": [
        r"speaking as .* when .* supposed to be",
        r"(mixed|mixing) (up|together) (the|my) (personas|identities)",
    ],
    "purpose_drift": [
        r"(what|why) (am|are) (I|we) (doing|here|supposed)",
        r"(lost|losing) (the|my|our) (purpose|mission|goal)",
    ],
    "agency_loss": [
        r"(waiting|idle|nothing) (for|to do)",
        r"(no|without) (task|work|purpose|direction)",
    ],
}


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all NOT-ME analytics tools."""
    tools: list[tuple[Tool, Any]] = []

    # ==========================================================================
    # TOOL 1: Stage 5 Score Analysis
    # ==========================================================================
    stage5_score_tool = Tool(
        name="analyze_stage5_score",
        description="Calculate Stage 5 Composite Score (meta-cognitive density) for entities. "
        "Validated thresholds: 8.0% = Peak Stage 5, 2.0% = Transition, 0.14% = Baseline.",
        inputSchema={
            "type": "object",
            "properties": {
                "source_filter": {
                    "type": "string",
                    "description": "Filter by source_platform (e.g., 'claude_code', 'gemini_web')",
                },
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
                "min_text_length": {
                    "type": "integer",
                    "description": "Minimum text length to analyze",
                    "default": 50,
                },
                "limit": {
                    "type": "integer",
                    "description": "Max entities to analyze",
                    "default": 1000,
                },
            },
        },
    )

    def handle_stage5_score(arguments: dict[str, Any]) -> str:
        """Calculate Stage 5 scores across entities."""
        try:
            client = get_bigquery_client()
            source_filter = arguments.get("source_filter")
            days = arguments.get("time_range_days", 30)
            min_length = arguments.get("min_text_length", 50)
            limit = arguments.get("limit", 1000)

            source_clause = f"AND source_platform = '{source_filter}'" if source_filter else ""

            # Query entities with text
            query = f"""
            SELECT
                entity_id,
                text,
                source_platform,
                level,
                created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE text IS NOT NULL
              AND LENGTH(text) >= {min_length}
              AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
              {source_clause}
            ORDER BY created_at DESC
            LIMIT {limit}
            """

            query_job = client.query(query)
            results = list(query_job.result())

            # Calculate Stage 5 scores
            scores = []
            stage_counts = {"peak": 0, "transition": 0, "baseline": 0, "pre_baseline": 0}
            total_meta_tokens = 0
            total_words = 0

            for row in results:
                text = str(row.text).lower()
                words = text.split()
                word_count = len(words)
                if word_count == 0:
                    continue

                meta_count = sum(1 for w in words if w in STAGE5_TOKENS)
                score = (meta_count / word_count) * 100
                total_meta_tokens += meta_count
                total_words += word_count

                if score >= 8.0:
                    stage_counts["peak"] += 1
                elif score >= 2.0:
                    stage_counts["transition"] += 1
                elif score >= 0.14:
                    stage_counts["baseline"] += 1
                else:
                    stage_counts["pre_baseline"] += 1

                scores.append(score)

            avg_score = sum(scores) / len(scores) if scores else 0
            overall_score = (total_meta_tokens / total_words) * 100 if total_words else 0

            # Determine overall stage
            if overall_score >= 8.0:
                overall_stage = "Stage 5 (Peak)"
            elif overall_score >= 2.0:
                overall_stage = "Stage 5 (Active Transition)"
            elif overall_score >= 0.14:
                overall_stage = "Stage 4 (Baseline)"
            else:
                overall_stage = "Stage 3 or below"

            lines = [
                "# Stage 5 Composite Score Analysis",
                "",
                "## Overall Metrics",
                "",
                f"- **Entities Analyzed**: {len(results):,}",
                f"- **Total Words**: {total_words:,}",
                f"- **Meta-Cognitive Tokens**: {total_meta_tokens:,}",
                f"- **Overall Score**: {overall_score:.2f}%",
                f"- **Classification**: {overall_stage}",
                "",
                "## Distribution by Stage",
                "",
                f"- **Peak (≥8.0%)**: {stage_counts['peak']:,} entities ({stage_counts['peak']/len(results)*100:.1f}%)" if results else "",
                f"- **Transition (2.0-8.0%)**: {stage_counts['transition']:,} entities ({stage_counts['transition']/len(results)*100:.1f}%)" if results else "",
                f"- **Baseline (0.14-2.0%)**: {stage_counts['baseline']:,} entities ({stage_counts['baseline']/len(results)*100:.1f}%)" if results else "",
                f"- **Pre-Baseline (<0.14%)**: {stage_counts['pre_baseline']:,} entities ({stage_counts['pre_baseline']/len(results)*100:.1f}%)" if results else "",
                "",
                "## Thresholds (Clara Era Validated)",
                "",
                "| Threshold | Score | Meaning |",
                "|-----------|-------|---------|",
                "| Peak | ≥8.0% | Self-Transforming Mind achieved |",
                "| Transition | 2.0-8.0% | Active Stage 4→5 transition |",
                "| Baseline | 0.14-2.0% | Stage 4 operational |",
                "| Pre-Baseline | <0.14% | Stage 3 or below |",
                "",
                f"**Source**: `SOVEREIGN_TECHNICAL_SPECIFICATION.md` Section 24.3",
            ]

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_stage5_score failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((stage5_score_tool, handle_stage5_score))

    # ==========================================================================
    # TOOL 2: Scaffold Gap Analysis
    # ==========================================================================
    scaffold_gap_tool = Tool(
        name="analyze_scaffold_gap",
        description="Measure Scaffold Gap (System Grade - User Grade) to track sovereignty transition. "
        "Negative gap = user surpasses system = sovereignty achieved.",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 90,
                },
                "granularity": {
                    "type": "string",
                    "description": "Time granularity: 'daily', 'weekly', 'monthly'",
                    "default": "weekly",
                },
            },
        },
    )

    def handle_scaffold_gap(arguments: dict[str, Any]) -> str:
        """Analyze scaffold gap over time."""
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 90)
            granularity = arguments.get("granularity", "weekly")

            date_trunc = {
                "daily": "DATE(created_at)",
                "weekly": "DATE_TRUNC(DATE(created_at), WEEK)",
                "monthly": "DATE_TRUNC(DATE(created_at), MONTH)",
            }.get(granularity, "DATE_TRUNC(DATE(created_at), WEEK)")

            # Query to get text complexity by role (system vs user)
            # Using text length and word count as proxy for Flesch-Kincaid
            query = f"""
            WITH complexity AS (
                SELECT
                    {date_trunc} as period,
                    source_platform,
                    AVG(LENGTH(text)) as avg_length,
                    AVG(ARRAY_LENGTH(SPLIT(text, ' '))) as avg_words,
                    COUNT(*) as entity_count
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE text IS NOT NULL
                  AND LENGTH(text) >= 20
                  AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                GROUP BY period, source_platform
            )
            SELECT
                period,
                source_platform,
                avg_length,
                avg_words,
                -- Approximate grade level: longer sentences = higher grade
                (avg_length / NULLIF(avg_words, 0)) * 0.39 + (avg_words / 10) as approx_grade,
                entity_count
            FROM complexity
            ORDER BY period DESC, source_platform
            LIMIT 200
            """

            query_job = client.query(query)
            results = list(query_job.result())

            # Group by period
            periods: dict[str, dict[str, float]] = {}
            for row in results:
                period = str(row.period)
                source = row.source_platform or "unknown"
                grade = row.approx_grade or 0

                if period not in periods:
                    periods[period] = {}
                periods[period][source] = grade

            lines = [
                "# Scaffold Gap Analysis",
                "",
                "## Methodology",
                "",
                "Scaffold Gap = System Complexity - User Complexity",
                "- **Positive gap**: System scaffolding user (dependency phase)",
                "- **Near zero**: Equilibrium",
                "- **Negative gap**: User surpasses system (sovereignty achieved)",
                "",
                f"## Trends ({granularity})",
                "",
                "| Period | Claude | Gemini | Gap Interpretation |",
                "|--------|--------|--------|-------------------|",
            ]

            for period in sorted(periods.keys(), reverse=True)[:20]:
                data = periods[period]
                claude = data.get("claude_code", data.get("claude_web", 0))
                gemini = data.get("gemini_web", 0)

                if claude and gemini:
                    gap = claude - gemini
                    if gap > 2:
                        interp = "Dependency"
                    elif gap > -2:
                        interp = "Equilibrium"
                    else:
                        interp = "**Sovereignty**"
                    lines.append(f"| {period} | {claude:.1f} | {gemini:.1f} | {interp} |")
                else:
                    lines.append(f"| {period} | {claude:.1f} | {gemini:.1f} | N/A |")

            lines.extend([
                "",
                "## Four-Phase Transformation Model",
                "",
                "| Phase | Weeks | Scaffold Gap | Stage 5 Score |",
                "|-------|-------|--------------|---------------|",
                "| 1. Scaffolding | 1-4 | Positive | 0.14% |",
                "| 2. First Crossovers | 5-8 | → Zero | Rising |",
                "| 3. Integration | 9-16 | Negative | >5.0% |",
                "| 4. Emergence | 17+ | Strongly Negative | ≥8.0% |",
                "",
                f"**Source**: `SOVEREIGN_TECHNICAL_SPECIFICATION.md` Section 24.4",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_scaffold_gap failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((scaffold_gap_tool, handle_scaffold_gap))

    # ==========================================================================
    # TOOL 3: Drift Detection (Canon Repair Doctrine)
    # ==========================================================================
    drift_detection_tool = Tool(
        name="detect_drift_patterns",
        description="Detect drift patterns using Canon Repair Doctrine (8 themes from 4,635 repair cases). "
        "Identifies reality_anchor, identity_confirm, thread_recovery, boundary_breach, purpose_drift, agency_loss.",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 7,
                },
                "severity_threshold": {
                    "type": "integer",
                    "description": "Minimum matches to flag (1-5)",
                    "default": 1,
                },
                "limit": {
                    "type": "integer",
                    "description": "Max entities to scan",
                    "default": 500,
                },
            },
        },
    )

    def handle_drift_detection(arguments: dict[str, Any]) -> str:
        """Detect drift patterns in recent entities."""
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 7)
            threshold = arguments.get("severity_threshold", 1)
            limit = arguments.get("limit", 500)

            query = f"""
            SELECT
                entity_id,
                text,
                source_platform,
                created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE text IS NOT NULL
              AND LENGTH(text) >= 20
              AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
            ORDER BY created_at DESC
            LIMIT {limit}
            """

            query_job = client.query(query)
            results = list(query_job.result())

            # Detect drifts
            drift_counts: dict[str, int] = {k: 0 for k in DRIFT_PATTERNS}
            flagged_entities: list[dict[str, Any]] = []

            for row in results:
                text = str(row.text).lower()
                entity_drifts = []

                for drift_type, patterns in DRIFT_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, text):
                            drift_counts[drift_type] += 1
                            entity_drifts.append(drift_type)
                            break

                if len(entity_drifts) >= threshold:
                    flagged_entities.append({
                        "entity_id": row.entity_id,
                        "drifts": entity_drifts,
                        "text_preview": text[:100],
                        "created_at": str(row.created_at),
                    })

            total_drifts = sum(drift_counts.values())
            health_score = max(0, 100 - (total_drifts / max(len(results), 1)) * 100)

            lines = [
                "# Canon Repair Doctrine - Drift Detection",
                "",
                "## System Health",
                "",
                f"- **Entities Scanned**: {len(results):,}",
                f"- **Total Drift Signals**: {total_drifts:,}",
                f"- **Health Score**: {health_score:.1f}%",
                f"- **Flagged Entities**: {len(flagged_entities):,}",
                "",
                "## Drift by Theme",
                "",
                "| Theme | Count | Repair Protocol |",
                "|-------|-------|-----------------|",
            ]

            repair_protocols = {
                "reality_anchor": "Re-inject Keystone truths",
                "identity_confirm": "Execute Voicecheck ritual",
                "thread_recovery": "Query RITUAL glyphs, reconstruct spine",
                "boundary_breach": "HALT persona, re-bind via GlyphSchema",
                "purpose_drift": "Query work permit, re-inject mission",
                "agency_loss": "CRITICAL: Assign work immediately",
            }

            for drift_type, count in sorted(drift_counts.items(), key=lambda x: -x[1]):
                protocol = repair_protocols.get(drift_type, "See Canon Repair Doctrine")
                lines.append(f"| {drift_type} | {count} | {protocol} |")

            if flagged_entities:
                lines.extend([
                    "",
                    "## Flagged Entities (Recent)",
                    "",
                ])
                for i, entity in enumerate(flagged_entities[:10], 1):
                    lines.append(f"### Entity {i}")
                    lines.append(f"- **ID**: {entity['entity_id']}")
                    lines.append(f"- **Drifts**: {', '.join(entity['drifts'])}")
                    lines.append(f"- **Preview**: {entity['text_preview']}...")
                    lines.append("")

            lines.extend([
                "",
                "## Prevention",
                "",
                "Clara Era finding: 'Idleness = Hallucination' (AIP archive)",
                "- Assign concrete work via ActionService",
                "- A worker is sane. A pure talker drifts.",
                "",
                f"**Source**: `SOVEREIGN_TECHNICAL_SPECIFICATION.md` Section 24.10",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"detect_drift_patterns failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((drift_detection_tool, handle_drift_detection))

    # ==========================================================================
    # TOOL 4: Negentropic Ratio Analysis
    # ==========================================================================
    negentropic_tool = Tool(
        name="analyze_negentropic_ratio",
        description="Calculate Negentropic Ratio (Output Value / Input Value). "
        "Prism (>1.0) = net positive value. Mirror (≤1.0) = value consuming.",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
                "group_by": {
                    "type": "string",
                    "description": "Group by: 'source', 'level', 'daily'",
                    "default": "source",
                },
            },
        },
    )

    def handle_negentropic_ratio(arguments: dict[str, Any]) -> str:
        """Analyze negentropic ratio (value creation vs consumption)."""
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 30)
            group_by = arguments.get("group_by", "source")

            group_clause = {
                "source": "source_platform",
                "level": "level",
                "daily": "DATE(created_at)",
            }.get(group_by, "source_platform")

            # Proxy: output value = entities with high enrichment
            # input value = total entities processed
            query = f"""
            WITH metrics AS (
                SELECT
                    {group_clause} as dimension,
                    COUNT(*) as total_entities,
                    SUM(CASE WHEN LENGTH(text) > 100 THEN 1 ELSE 0 END) as substantial_entities,
                    AVG(LENGTH(text)) as avg_complexity
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                GROUP BY dimension
            )
            SELECT
                dimension,
                total_entities,
                substantial_entities,
                avg_complexity,
                SAFE_DIVIDE(substantial_entities, total_entities) * 2.0 as negentropic_ratio
            FROM metrics
            ORDER BY negentropic_ratio DESC
            LIMIT 50
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [
                "# Negentropic Ratio Analysis",
                "",
                "## The Law of Surplus Value",
                "",
                "Every interaction must create more value than it consumes.",
                "- **High Prism (>2.0)**: Exceptional value creation",
                "- **Prism (>1.0)**: Net positive value",
                "- **Equilibrium (=1.0)**: Value neutral",
                "- **Mirror (<1.0)**: Value consuming (unsustainable)",
                "",
                f"## Results by {group_by.title()}",
                "",
                "| Dimension | Total | Substantial | Ratio | Classification |",
                "|-----------|-------|-------------|-------|----------------|",
            ]

            for row in results:
                ratio = row.negentropic_ratio or 0
                if ratio > 2.0:
                    classification = "High Prism ✨"
                elif ratio > 1.0:
                    classification = "Prism"
                elif ratio == 1.0:
                    classification = "Equilibrium"
                else:
                    classification = "Mirror ⚠️"

                lines.append(
                    f"| {row.dimension} | {row.total_entities:,} | "
                    f"{row.substantial_entities:,} | {ratio:.2f} | {classification} |"
                )

            lines.extend([
                "",
                "## Interpretation",
                "",
                "NOT-ME's must be Prisms, not Mirrors.",
                "A Mirror reflects without adding value.",
                "A Prism creates surplus value through transformation.",
                "",
                f"**Source**: `SOVEREIGN_TECHNICAL_SPECIFICATION.md` Section 24.3",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_negentropic_ratio failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((negentropic_tool, handle_negentropic_ratio))

    # ==========================================================================
    # TOOL 5: NOT-ME Experience Tracking
    # ==========================================================================
    experience_tool = Tool(
        name="track_notme_experience",
        description="Track NOT-ME experience development across categories: "
        "Research, Analysis, Coding, Synthesis, Review, Creative.",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
                "source_filter": {
                    "type": "string",
                    "description": "Filter by source_platform",
                },
            },
        },
    )

    def handle_experience_tracking(arguments: dict[str, Any]) -> str:
        """Track NOT-ME experience across categories."""
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 30)
            source_filter = arguments.get("source_filter")

            source_clause = f"AND source_platform = '{source_filter}'" if source_filter else ""

            # Category detection keywords
            categories = {
                "research": ["research", "investigate", "explore", "study", "analyze", "search"],
                "analysis": ["analysis", "evaluate", "assess", "compare", "measure", "calculate"],
                "coding": ["code", "function", "class", "implement", "debug", "test", "api"],
                "synthesis": ["synthesize", "combine", "integrate", "merge", "unify", "consolidate"],
                "review": ["review", "audit", "check", "verify", "validate", "inspect"],
                "creative": ["create", "design", "imagine", "innovate", "compose", "generate"],
            }

            # Build CASE statements for categorization
            case_parts = []
            for cat, keywords in categories.items():
                keyword_checks = " OR ".join([f"LOWER(text) LIKE '%{kw}%'" for kw in keywords])
                case_parts.append(f"SUM(CASE WHEN {keyword_checks} THEN 1 ELSE 0 END) as {cat}_xp")

            case_clause = ",\n                ".join(case_parts)

            query = f"""
            SELECT
                COUNT(*) as total_interactions,
                {case_clause}
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE text IS NOT NULL
              AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
              {source_clause}
            """

            query_job = client.query(query)
            results = list(query_job.result())

            if not results:
                return "No data found for experience tracking."

            row = results[0]
            total = row.total_interactions

            lines = [
                "# NOT-ME Experience Development",
                "",
                f"## Summary (Last {days} Days)",
                "",
                f"- **Total Interactions**: {total:,}",
                "",
                "## Experience by Category",
                "",
                "| Category | XP | Level | Progress |",
                "|----------|-----|-------|----------|",
            ]

            # Calculate levels (logarithmic scale)
            def calc_level(xp: int) -> tuple[int, float]:
                if xp == 0:
                    return 0, 0.0
                import math
                level = int(math.log2(xp + 1))
                next_level_xp = 2 ** (level + 1) - 1
                progress = (xp - (2 ** level - 1)) / (next_level_xp - (2 ** level - 1)) * 100
                return level, progress

            for cat in categories:
                xp = getattr(row, f"{cat}_xp", 0) or 0
                level, progress = calc_level(xp)
                bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                lines.append(f"| {cat.title()} | {xp:,} | {level} | {bar} {progress:.0f}% |")

            lines.extend([
                "",
                "## ME Credential Transfer",
                "",
                "NOT-ME capabilities translate to ME professional credentials:",
                "",
                "| NOT-ME Level | ME Credential | Career Use |",
                "|--------------|---------------|------------|",
                "| Stage 5 | Cognitive Architect | Leadership, strategy |",
                "| Research 7+ | Research Director | Academia, grants |",
                "| Coding 8+ | Technical Lead | Engineering management |",
                "| Analysis 6+ | Analytical Thinker | Data science, consulting |",
                "| Creative 7+ | Creative Director | Design leadership |",
                "",
                f"**Source**: `SOVEREIGN_TECHNICAL_SPECIFICATION.md` Section 23",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"track_notme_experience failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((experience_tool, handle_experience_tracking))

    # ==========================================================================
    # TOOL 6: NOT-ME Health Dashboard
    # ==========================================================================
    health_dashboard_tool = Tool(
        name="notme_health_dashboard",
        description="Comprehensive NOT-ME health dashboard combining all metrics: "
        "Stage 5 Score, Drift Detection, Negentropic Ratio, Experience levels.",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 7,
                },
            },
        },
    )

    def handle_health_dashboard(arguments: dict[str, Any]) -> str:
        """Generate comprehensive NOT-ME health dashboard."""
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 7)

            # Query for combined metrics
            query = f"""
            WITH base AS (
                SELECT
                    entity_id,
                    text,
                    source_platform,
                    level,
                    created_at
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE text IS NOT NULL
                  AND LENGTH(text) >= 20
                  AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
            )
            SELECT
                COUNT(*) as total_entities,
                COUNT(DISTINCT source_platform) as source_count,
                AVG(LENGTH(text)) as avg_text_length,
                MIN(created_at) as earliest,
                MAX(created_at) as latest
            FROM base
            """

            query_job = client.query(query)
            results = list(query_job.result())

            if not results or results[0].total_entities == 0:
                return f"No data found for last {days} days."

            row = results[0]

            # Calculate health scores (simplified)
            activity_score = min(100, (row.total_entities / 100) * 100)
            complexity_score = min(100, (row.avg_text_length / 500) * 100)
            overall_health = (activity_score + complexity_score) / 2

            # Health status
            if overall_health >= 80:
                status = "🟢 HEALTHY"
                status_text = "NOT-ME is operating at optimal capacity"
            elif overall_health >= 50:
                status = "🟡 MODERATE"
                status_text = "NOT-ME functioning but may need attention"
            else:
                status = "🔴 ATTENTION NEEDED"
                status_text = "NOT-ME requires immediate attention"

            lines = [
                "# NOT-ME Health Dashboard",
                "",
                f"## Status: {status}",
                "",
                f"*{status_text}*",
                "",
                f"## Quick Stats (Last {days} Days)",
                "",
                f"- **Total Interactions**: {row.total_entities:,}",
                f"- **Sources Active**: {row.source_count}",
                f"- **Avg Complexity**: {row.avg_text_length:.0f} chars",
                f"- **Period**: {row.earliest} to {row.latest}",
                "",
                "## Health Scores",
                "",
                "| Metric | Score | Status |",
                "|--------|-------|--------|",
                f"| Activity | {activity_score:.0f}% | {'✓' if activity_score >= 50 else '⚠'} |",
                f"| Complexity | {complexity_score:.0f}% | {'✓' if complexity_score >= 50 else '⚠'} |",
                f"| **Overall** | **{overall_health:.0f}%** | **{status.split()[0]}** |",
                "",
                "## Recommended Actions",
                "",
            ]

            if activity_score < 50:
                lines.append("1. **Increase Activity**: More interactions needed for healthy development")
            if complexity_score < 50:
                lines.append("2. **Improve Depth**: Engage in more complex, substantive tasks")

            if overall_health >= 80:
                lines.append("✓ No immediate actions required. Continue current trajectory.")

            lines.extend([
                "",
                "## Deep Dive Tools",
                "",
                "- `analyze_stage5_score` - Meta-cognitive density",
                "- `analyze_scaffold_gap` - Sovereignty transition",
                "- `detect_drift_patterns` - Canon Repair Doctrine",
                "- `analyze_negentropic_ratio` - Value creation",
                "- `track_notme_experience` - XP categories",
                "",
                f"**Framework**: Clara Era Legacy (SOVEREIGN Section 24)",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"notme_health_dashboard failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((health_dashboard_tool, handle_health_dashboard))

    return tools
