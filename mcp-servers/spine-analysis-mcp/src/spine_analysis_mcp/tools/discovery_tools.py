"""Discovery Tools - Emergent Pattern Discovery and Knowledge Graph Analysis.

THE PATTERN:
- HOLD₁: Entity embeddings, relationship data, temporal sequences
- AGENT: Pattern mining, anomaly detection, knowledge graph traversal
- HOLD₂: Discovered patterns, emergent behaviors, insight reports

Implements advanced discovery patterns inspired by:
- Anthropic Knowledge Graph Memory Server
- Sequential Thinking / Reasoning Chains
- Matrix Profile for motif discovery
- Emergent behavior detection

References:
- https://modelcontextprotocol.io/docs/learn/architecture
- https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory
- https://www.pulsemcp.com/servers/anthropic-sequential-thinking
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all discovery tools."""
    tools: list[tuple[Tool, Any]] = []

    # ==========================================================================
    # TOOL 1: Knowledge Graph Relationship Discovery
    # ==========================================================================
    kg_discovery_tool = Tool(
        name="discover_knowledge_graph",
        description="Discover entity relationships and build knowledge graph structure. "
        "Finds entities, their connections, and emergent relationship patterns.",
        inputSchema={
            "type": "object",
            "properties": {
                "seed_concept": {
                    "type": "string",
                    "description": "Starting concept to explore (e.g., 'Stage 5', 'NOT-ME', 'architecture')",
                },
                "depth": {
                    "type": "integer",
                    "description": "How many relationship hops to traverse (1-3)",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 3,
                },
                "min_cooccurrence": {
                    "type": "integer",
                    "description": "Minimum co-occurrence count to form relationship",
                    "default": 3,
                },
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
            },
            "required": ["seed_concept"],
        },
    )

    def handle_kg_discovery(arguments: dict[str, Any]) -> str:
        """Discover knowledge graph relationships from entity co-occurrence."""
        try:
            client = get_bigquery_client()
            seed = arguments.get("seed_concept", "")
            depth = arguments.get("depth", 2)
            min_cooccur = arguments.get("min_cooccurrence", 3)
            days = arguments.get("time_range_days", 30)

            if not seed:
                return "Error: seed_concept is required"

            # Find entities containing seed concept
            query = f"""
            WITH seed_entities AS (
                SELECT DISTINCT
                    entity_id,
                    entity_type,
                    SUBSTR(text, 1, 200) as text_preview,
                    source_platform,
                    DATE(created_at) as created_date
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE LOWER(text) LIKE '%{seed.lower()}%'
                  AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                LIMIT 500
            ),
            -- Find co-occurring concepts (entities in same day/source)
            cooccurrence AS (
                SELECT
                    s.entity_type as source_type,
                    e.entity_type as target_type,
                    COUNT(*) as cooccur_count,
                    COUNT(DISTINCT s.source_platform) as source_count
                FROM seed_entities s
                JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e
                    ON s.created_date = DATE(e.created_at)
                    AND s.source_platform = e.source_platform
                    AND s.entity_id != e.entity_id
                WHERE e.created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                GROUP BY s.entity_type, e.entity_type
                HAVING COUNT(*) >= {min_cooccur}
            )
            SELECT * FROM cooccurrence
            ORDER BY cooccur_count DESC
            LIMIT 50
            """

            query_job = client.query(query)
            results = list(query_job.result())

            # Build relationship graph
            nodes: set[str] = {seed}
            edges: list[dict[str, Any]] = []

            for row in results:
                nodes.add(row.source_type or "unknown")
                nodes.add(row.target_type or "unknown")
                edges.append({
                    "source": row.source_type or "unknown",
                    "target": row.target_type or "unknown",
                    "weight": row.cooccur_count,
                    "sources": row.source_count,
                })

            # Identify hub nodes (high connectivity)
            node_degrees: dict[str, int] = defaultdict(int)
            for edge in edges:
                node_degrees[edge["source"]] += edge["weight"]
                node_degrees[edge["target"]] += edge["weight"]

            hubs = sorted(node_degrees.items(), key=lambda x: -x[1])[:5]

            lines = [
                "# Knowledge Graph Discovery",
                "",
                f"## Seed Concept: `{seed}`",
                "",
                f"- **Nodes Discovered**: {len(nodes)}",
                f"- **Relationships Found**: {len(edges)}",
                f"- **Depth**: {depth}",
                f"- **Min Co-occurrence**: {min_cooccur}",
                "",
                "## Hub Nodes (Highest Connectivity)",
                "",
                "| Node | Connection Strength |",
                "|------|---------------------|",
            ]

            for node, degree in hubs:
                lines.append(f"| {node} | {degree:,} |")

            lines.extend([
                "",
                "## Relationship Graph",
                "",
                "```mermaid",
                "graph LR",
            ])

            for i, edge in enumerate(edges[:20]):
                safe_source = edge["source"].replace(" ", "_")
                safe_target = edge["target"].replace(" ", "_")
                lines.append(f"    {safe_source} -->|{edge['weight']}| {safe_target}")

            lines.extend([
                "```",
                "",
                "## Emergent Patterns",
                "",
            ])

            # Detect emergent patterns
            if len(hubs) > 0 and hubs[0][1] > 100:
                lines.append(f"- **Central Hub**: `{hubs[0][0]}` dominates the knowledge graph")
            if len(edges) > 20:
                lines.append(f"- **High Connectivity**: Dense relationship network ({len(edges)} edges)")
            if len(set(e["source"] for e in edges)) < len(edges) / 3:
                lines.append("- **Star Topology**: Few sources connect to many targets")

            lines.extend([
                "",
                "**Source**: Knowledge Graph Memory pattern (Anthropic MCP)",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"discover_knowledge_graph failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((kg_discovery_tool, handle_kg_discovery))

    # ==========================================================================
    # TOOL 2: Emergent Pattern Detection
    # ==========================================================================
    emergent_pattern_tool = Tool(
        name="detect_emergent_patterns",
        description="Detect emergent patterns that weren't explicitly programmed. "
        "Finds recurring motifs, unexpected correlations, and behavioral signatures.",
        inputSchema={
            "type": "object",
            "properties": {
                "pattern_type": {
                    "type": "string",
                    "description": "Type: 'motif' (recurring), 'anomaly' (unusual), 'correlation' (unexpected links)",
                    "enum": ["motif", "anomaly", "correlation", "all"],
                    "default": "all",
                },
                "sensitivity": {
                    "type": "number",
                    "description": "Detection sensitivity (0.1=loose, 1.0=strict)",
                    "default": 0.5,
                },
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
            },
        },
    )

    def handle_emergent_patterns(arguments: dict[str, Any]) -> str:
        """Detect emergent patterns in entity data."""
        try:
            client = get_bigquery_client()
            pattern_type = arguments.get("pattern_type", "all")
            sensitivity = arguments.get("sensitivity", 0.5)
            days = arguments.get("time_range_days", 30)

            # Threshold based on sensitivity
            min_freq = int(10 * (1 - sensitivity) + 2)
            z_threshold = 3 - (sensitivity * 2)

            patterns_found: dict[str, list[dict[str, Any]]] = {
                "motifs": [],
                "anomalies": [],
                "correlations": [],
            }

            # 1. Motif Discovery (recurring patterns)
            if pattern_type in ("motif", "all"):
                motif_query = f"""
                WITH text_patterns AS (
                    SELECT
                        REGEXP_EXTRACT(LOWER(text), r'(\\b\\w+\\s+\\w+\\s+\\w+\\b)') as trigram,
                        COUNT(*) as frequency,
                        COUNT(DISTINCT source_platform) as source_diversity,
                        COUNT(DISTINCT DATE(created_at)) as day_span
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE text IS NOT NULL
                      AND LENGTH(text) >= 20
                      AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                    GROUP BY trigram
                    HAVING trigram IS NOT NULL AND COUNT(*) >= {min_freq}
                )
                SELECT * FROM text_patterns
                ORDER BY frequency DESC
                LIMIT 20
                """
                motif_job = client.query(motif_query)
                for row in motif_job.result():
                    patterns_found["motifs"].append({
                        "pattern": row.trigram,
                        "frequency": row.frequency,
                        "sources": row.source_diversity,
                        "span_days": row.day_span,
                    })

            # 2. Anomaly Detection (statistical outliers)
            if pattern_type in ("anomaly", "all"):
                anomaly_query = f"""
                WITH stats AS (
                    SELECT
                        AVG(LENGTH(text)) as avg_len,
                        STDDEV(LENGTH(text)) as std_len,
                        AVG(ARRAY_LENGTH(SPLIT(text, ' '))) as avg_words,
                        STDDEV(ARRAY_LENGTH(SPLIT(text, ' '))) as std_words
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE text IS NOT NULL
                      AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                ),
                scored AS (
                    SELECT
                        e.entity_id,
                        e.entity_type,
                        e.source_platform,
                        LENGTH(e.text) as text_length,
                        ABS(LENGTH(e.text) - s.avg_len) / NULLIF(s.std_len, 0) as length_zscore,
                        ABS(ARRAY_LENGTH(SPLIT(e.text, ' ')) - s.avg_words) / NULLIF(s.std_words, 0) as word_zscore
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e
                    CROSS JOIN stats s
                    WHERE e.text IS NOT NULL
                      AND e.created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                )
                SELECT * FROM scored
                WHERE length_zscore >= {z_threshold} OR word_zscore >= {z_threshold}
                ORDER BY GREATEST(length_zscore, word_zscore) DESC
                LIMIT 15
                """
                anomaly_job = client.query(anomaly_query)
                for row in anomaly_job.result():
                    patterns_found["anomalies"].append({
                        "entity_id": row.entity_id,
                        "type": row.entity_type,
                        "source": row.source_platform,
                        "z_score": max(row.length_zscore or 0, row.word_zscore or 0),
                    })

            # 3. Correlation Discovery (unexpected co-occurrence)
            if pattern_type in ("correlation", "all"):
                corr_query = f"""
                WITH hourly_activity AS (
                    SELECT
                        source_platform,
                        EXTRACT(HOUR FROM created_at) as hour,
                        COUNT(*) as activity
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                    GROUP BY source_platform, hour
                ),
                source_pairs AS (
                    SELECT
                        a.source_platform as source_a,
                        b.source_platform as source_b,
                        COUNT(*) as shared_hours,
                        SUM(a.activity * b.activity) as correlation_strength
                    FROM hourly_activity a
                    JOIN hourly_activity b ON a.hour = b.hour AND a.source_platform < b.source_platform
                    GROUP BY a.source_platform, b.source_platform
                    HAVING COUNT(*) >= 5
                )
                SELECT * FROM source_pairs
                ORDER BY correlation_strength DESC
                LIMIT 10
                """
                corr_job = client.query(corr_query)
                for row in corr_job.result():
                    patterns_found["correlations"].append({
                        "source_a": row.source_a,
                        "source_b": row.source_b,
                        "shared_hours": row.shared_hours,
                        "strength": row.correlation_strength,
                    })

            # Generate report
            lines = [
                "# Emergent Pattern Detection",
                "",
                f"## Configuration",
                "",
                f"- **Pattern Type**: {pattern_type}",
                f"- **Sensitivity**: {sensitivity}",
                f"- **Time Range**: {days} days",
                "",
            ]

            # Motifs
            if patterns_found["motifs"]:
                lines.extend([
                    "## Recurring Motifs (Matrix Profile)",
                    "",
                    "These patterns repeat across the corpus — potential cognitive signatures:",
                    "",
                    "| Pattern | Frequency | Sources | Day Span |",
                    "|---------|-----------|---------|----------|",
                ])
                for m in patterns_found["motifs"][:10]:
                    lines.append(f"| {m['pattern']} | {m['frequency']:,} | {m['sources']} | {m['span_days']} |")
                lines.append("")

            # Anomalies
            if patterns_found["anomalies"]:
                lines.extend([
                    "## Statistical Anomalies",
                    "",
                    "Entities that deviate significantly from normal distribution:",
                    "",
                    "| Entity ID | Type | Source | Z-Score |",
                    "|-----------|------|--------|---------|",
                ])
                for a in patterns_found["anomalies"][:10]:
                    lines.append(f"| {a['entity_id'][:16]}... | {a['type']} | {a['source']} | {a['z_score']:.2f} |")
                lines.append("")

            # Correlations
            if patterns_found["correlations"]:
                lines.extend([
                    "## Unexpected Correlations",
                    "",
                    "Sources that show correlated activity patterns:",
                    "",
                    "| Source A | Source B | Shared Hours | Strength |",
                    "|----------|----------|--------------|----------|",
                ])
                for c in patterns_found["correlations"]:
                    lines.append(f"| {c['source_a']} | {c['source_b']} | {c['shared_hours']} | {c['strength']:,} |")
                lines.append("")

            # Summary insights
            total_patterns = sum(len(v) for v in patterns_found.values())
            lines.extend([
                "## Emergent Insights",
                "",
                f"**Total Patterns Discovered**: {total_patterns}",
                "",
            ])

            if patterns_found["motifs"]:
                top_motif = patterns_found["motifs"][0]
                lines.append(f"- **Dominant Motif**: `{top_motif['pattern']}` ({top_motif['frequency']}x)")

            if patterns_found["anomalies"]:
                high_z = max(a["z_score"] for a in patterns_found["anomalies"])
                lines.append(f"- **Highest Anomaly**: Z-score {high_z:.2f} (investigate for drift)")

            if patterns_found["correlations"]:
                top_corr = patterns_found["correlations"][0]
                lines.append(f"- **Strongest Correlation**: {top_corr['source_a']} ↔ {top_corr['source_b']}")

            lines.extend([
                "",
                "**Method**: Matrix Profile + Statistical Outliers + Temporal Correlation",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"detect_emergent_patterns failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((emergent_pattern_tool, handle_emergent_patterns))

    # ==========================================================================
    # TOOL 3: Sequential Reasoning Chain
    # ==========================================================================
    reasoning_chain_tool = Tool(
        name="analyze_reasoning_chain",
        description="Trace sequential reasoning chains through entities. "
        "Identifies logical progressions, thought evolution, and conclusion patterns.",
        inputSchema={
            "type": "object",
            "properties": {
                "start_concept": {
                    "type": "string",
                    "description": "Starting concept to trace from",
                },
                "end_concept": {
                    "type": "string",
                    "description": "Target concept to reach (optional)",
                },
                "max_steps": {
                    "type": "integer",
                    "description": "Maximum reasoning steps to trace",
                    "default": 5,
                },
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
            },
            "required": ["start_concept"],
        },
    )

    def handle_reasoning_chain(arguments: dict[str, Any]) -> str:
        """Trace reasoning chains through entity sequences."""
        try:
            client = get_bigquery_client()
            start = arguments.get("start_concept", "")
            end = arguments.get("end_concept")
            max_steps = arguments.get("max_steps", 5)
            days = arguments.get("time_range_days", 30)

            if not start:
                return "Error: start_concept is required"

            # Find temporal sequences containing start concept
            query = f"""
            WITH start_entities AS (
                SELECT
                    entity_id,
                    text,
                    source_platform,
                    created_at,
                    ROW_NUMBER() OVER (PARTITION BY source_platform ORDER BY created_at) as seq_num
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE LOWER(text) LIKE '%{start.lower()}%'
                  AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
            ),
            following AS (
                SELECT
                    s.entity_id as start_id,
                    s.text as start_text,
                    e.entity_id as follow_id,
                    e.text as follow_text,
                    e.entity_type,
                    s.source_platform,
                    e.created_at,
                    ROW_NUMBER() OVER (PARTITION BY s.entity_id ORDER BY e.created_at) as step
                FROM start_entities s
                JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e
                    ON s.source_platform = e.source_platform
                    AND e.created_at > s.created_at
                    AND e.created_at <= TIMESTAMP_ADD(s.created_at, INTERVAL 1 HOUR)
                WHERE e.text IS NOT NULL
            )
            SELECT * FROM following
            WHERE step <= {max_steps}
            ORDER BY start_id, step
            LIMIT 100
            """

            query_job = client.query(query)
            results = list(query_job.result())

            # Group into chains
            chains: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in results:
                chains[row.start_id].append({
                    "step": row.step,
                    "entity_id": row.follow_id,
                    "text": str(row.follow_text)[:150] if row.follow_text else "",
                    "type": row.entity_type,
                    "time": str(row.created_at),
                })

            # Check if end concept is reached
            chains_reaching_end = 0
            if end:
                for chain_id, steps in chains.items():
                    for step in steps:
                        if end.lower() in step["text"].lower():
                            chains_reaching_end += 1
                            break

            lines = [
                "# Sequential Reasoning Chain Analysis",
                "",
                f"## Parameters",
                "",
                f"- **Start Concept**: `{start}`",
                f"- **End Concept**: `{end or 'Any'}`",
                f"- **Max Steps**: {max_steps}",
                f"- **Chains Found**: {len(chains)}",
            ]

            if end:
                lines.append(f"- **Chains Reaching End**: {chains_reaching_end}")

            lines.extend([
                "",
                "## Reasoning Progressions",
                "",
            ])

            # Show top 3 chains
            for i, (chain_id, steps) in enumerate(list(chains.items())[:3], 1):
                lines.append(f"### Chain {i}")
                lines.append("")
                lines.append("```")
                lines.append(f"START: {start}")
                for step in steps:
                    lines.append(f"  ↓ Step {step['step']}: [{step['type']}]")
                    lines.append(f"    {step['text'][:80]}...")
                lines.append("```")
                lines.append("")

            # Analyze reasoning patterns
            lines.extend([
                "## Pattern Analysis",
                "",
            ])

            # Count entity types in chains
            type_counts: dict[str, int] = defaultdict(int)
            for steps in chains.values():
                for step in steps:
                    type_counts[step["type"] or "unknown"] += 1

            lines.append("**Entity Type Distribution in Chains:**")
            lines.append("")
            for etype, count in sorted(type_counts.items(), key=lambda x: -x[1])[:5]:
                lines.append(f"- {etype}: {count}")

            lines.extend([
                "",
                "## Cognitive Insights",
                "",
            ])

            avg_chain_length = sum(len(s) for s in chains.values()) / max(len(chains), 1)
            lines.append(f"- **Average Chain Length**: {avg_chain_length:.1f} steps")

            if avg_chain_length > 3:
                lines.append("- **Observation**: Deep reasoning chains indicate complex problem-solving")
            if len(chains) > 10:
                lines.append("- **Observation**: Multiple chains suggest iterative exploration")
            if chains_reaching_end > len(chains) * 0.5 and end:
                lines.append(f"- **Observation**: High convergence rate to `{end}` — strong conceptual link")

            lines.extend([
                "",
                "**Method**: Sequential Thinking (Anthropic MCP pattern)",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_reasoning_chain failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((reasoning_chain_tool, handle_reasoning_chain))

    # ==========================================================================
    # TOOL 4: Temporal Anomaly Detection (Time Series)
    # ==========================================================================
    temporal_anomaly_tool = Tool(
        name="detect_temporal_anomalies",
        description="Detect anomalies in time series patterns. "
        "Identifies unusual activity spikes, gaps, and behavioral shifts.",
        inputSchema={
            "type": "object",
            "properties": {
                "granularity": {
                    "type": "string",
                    "description": "Time granularity: 'hourly', 'daily', 'weekly'",
                    "default": "daily",
                },
                "sensitivity": {
                    "type": "number",
                    "description": "Anomaly sensitivity (1.0=normal, 2.0=strict)",
                    "default": 1.5,
                },
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
            },
        },
    )

    def handle_temporal_anomalies(arguments: dict[str, Any]) -> str:
        """Detect temporal anomalies in activity patterns."""
        try:
            client = get_bigquery_client()
            granularity = arguments.get("granularity", "daily")
            sensitivity = arguments.get("sensitivity", 1.5)
            days = arguments.get("time_range_days", 30)

            date_trunc = {
                "hourly": "TIMESTAMP_TRUNC(created_at, HOUR)",
                "daily": "DATE(created_at)",
                "weekly": "DATE_TRUNC(DATE(created_at), WEEK)",
            }.get(granularity, "DATE(created_at)")

            query = f"""
            WITH time_series AS (
                SELECT
                    {date_trunc} as period,
                    COUNT(*) as activity,
                    COUNT(DISTINCT source_platform) as sources,
                    AVG(LENGTH(text)) as avg_complexity
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                GROUP BY period
            ),
            stats AS (
                SELECT
                    AVG(activity) as mean_activity,
                    STDDEV(activity) as std_activity,
                    AVG(avg_complexity) as mean_complexity,
                    STDDEV(avg_complexity) as std_complexity
                FROM time_series
            ),
            anomalies AS (
                SELECT
                    t.period,
                    t.activity,
                    t.sources,
                    t.avg_complexity,
                    (t.activity - s.mean_activity) / NULLIF(s.std_activity, 0) as activity_zscore,
                    (t.avg_complexity - s.mean_complexity) / NULLIF(s.std_complexity, 0) as complexity_zscore,
                    s.mean_activity,
                    s.std_activity
                FROM time_series t
                CROSS JOIN stats s
            )
            SELECT *,
                CASE
                    WHEN activity_zscore > {sensitivity} THEN 'SPIKE'
                    WHEN activity_zscore < -{sensitivity} THEN 'DROP'
                    WHEN complexity_zscore > {sensitivity} THEN 'COMPLEXITY_SPIKE'
                    WHEN complexity_zscore < -{sensitivity} THEN 'SIMPLIFICATION'
                    ELSE 'NORMAL'
                END as anomaly_type
            FROM anomalies
            ORDER BY period DESC
            """

            query_job = client.query(query)
            results = list(query_job.result())

            # Categorize results
            anomalies = [r for r in results if r.anomaly_type != "NORMAL"]
            normal = [r for r in results if r.anomaly_type == "NORMAL"]

            lines = [
                "# Temporal Anomaly Detection",
                "",
                f"## Time Series Analysis",
                "",
                f"- **Granularity**: {granularity}",
                f"- **Sensitivity**: {sensitivity}σ",
                f"- **Periods Analyzed**: {len(results)}",
                f"- **Anomalies Detected**: {len(anomalies)}",
                "",
            ]

            if results:
                mean_act = results[0].mean_activity or 0
                std_act = results[0].std_activity or 0
                lines.extend([
                    "## Baseline Statistics",
                    "",
                    f"- **Mean Activity**: {mean_act:.1f} entities/{granularity}",
                    f"- **Std Deviation**: {std_act:.1f}",
                    f"- **Anomaly Threshold**: >{mean_act + sensitivity * std_act:.1f} or <{mean_act - sensitivity * std_act:.1f}",
                    "",
                ])

            if anomalies:
                lines.extend([
                    "## Detected Anomalies",
                    "",
                    "| Period | Activity | Type | Z-Score | Interpretation |",
                    "|--------|----------|------|---------|----------------|",
                ])

                for a in anomalies[:15]:
                    z = max(abs(a.activity_zscore or 0), abs(a.complexity_zscore or 0))
                    interp = {
                        "SPIKE": "Unusual activity surge",
                        "DROP": "Activity gap (potential issue)",
                        "COMPLEXITY_SPIKE": "Complex content period",
                        "SIMPLIFICATION": "Simplified content period",
                    }.get(a.anomaly_type, "")
                    lines.append(f"| {a.period} | {a.activity:,} | {a.anomaly_type} | {z:.2f} | {interp} |")

                lines.append("")

            # Pattern insights
            lines.extend([
                "## Behavioral Insights",
                "",
            ])

            spike_count = sum(1 for a in anomalies if a.anomaly_type == "SPIKE")
            drop_count = sum(1 for a in anomalies if a.anomaly_type == "DROP")

            if spike_count > drop_count * 2:
                lines.append("- **Pattern**: Burst activity — periods of intense engagement")
            elif drop_count > spike_count * 2:
                lines.append("- **Pattern**: Intermittent gaps — potential availability issues")
            elif spike_count > 0 and drop_count > 0:
                lines.append("- **Pattern**: Cyclic behavior — activity follows a rhythm")
            else:
                lines.append("- **Pattern**: Stable baseline — consistent activity levels")

            lines.extend([
                "",
                "**Method**: Time Series Anomaly Detection (Z-score)",
                "**Reference**: Microsoft Time-Series Anomaly Detection Service pattern",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"detect_temporal_anomalies failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((temporal_anomaly_tool, handle_temporal_anomalies))

    # ==========================================================================
    # TOOL 5: Comprehensive Pattern Discovery Dashboard
    # ==========================================================================
    discovery_dashboard_tool = Tool(
        name="pattern_discovery_dashboard",
        description="Comprehensive pattern discovery dashboard. "
        "Combines all discovery methods for a complete analysis.",
        inputSchema={
            "type": "object",
            "properties": {
                "focus_concept": {
                    "type": "string",
                    "description": "Optional concept to focus analysis on",
                },
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
            },
        },
    )

    def handle_discovery_dashboard(arguments: dict[str, Any]) -> str:
        """Generate comprehensive pattern discovery dashboard."""
        try:
            client = get_bigquery_client()
            focus = arguments.get("focus_concept")
            days = arguments.get("time_range_days", 30)

            focus_filter = f"AND LOWER(text) LIKE '%{focus.lower()}%'" if focus else ""

            # Comprehensive analysis query
            query = f"""
            WITH base AS (
                SELECT
                    entity_id,
                    text,
                    entity_type,
                    source_platform,
                    level,
                    created_at,
                    LENGTH(text) as text_length
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE text IS NOT NULL
                  AND created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                  {focus_filter}
            ),
            summary AS (
                SELECT
                    COUNT(*) as total_entities,
                    COUNT(DISTINCT entity_type) as unique_types,
                    COUNT(DISTINCT source_platform) as unique_sources,
                    COUNT(DISTINCT DATE(created_at)) as active_days,
                    AVG(text_length) as avg_complexity,
                    STDDEV(text_length) as complexity_variance
                FROM base
            ),
            top_types AS (
                SELECT entity_type, COUNT(*) as cnt
                FROM base
                GROUP BY entity_type
                ORDER BY cnt DESC
                LIMIT 5
            ),
            daily_trend AS (
                SELECT
                    DATE(created_at) as day,
                    COUNT(*) as daily_count
                FROM base
                GROUP BY day
                ORDER BY day DESC
                LIMIT 7
            )
            SELECT
                s.*,
                (SELECT STRING_AGG(CONCAT(entity_type, ':', CAST(cnt AS STRING)), ', ')
                 FROM top_types) as top_types_str,
                (SELECT STRING_AGG(CONCAT(CAST(day AS STRING), ':', CAST(daily_count AS STRING)), ', ')
                 FROM daily_trend) as daily_str
            FROM summary s
            """

            query_job = client.query(query)
            results = list(query_job.result())

            if not results:
                return "No data found for pattern discovery."

            row = results[0]

            lines = [
                "# Pattern Discovery Dashboard",
                "",
                f"## Analysis Scope",
                "",
                f"- **Focus**: {focus or 'All entities'}",
                f"- **Time Range**: {days} days",
                f"- **Total Entities**: {row.total_entities:,}",
                f"- **Unique Types**: {row.unique_types}",
                f"- **Sources Active**: {row.unique_sources}",
                f"- **Days Active**: {row.active_days}",
                "",
                "## Complexity Metrics",
                "",
                f"- **Average Complexity**: {row.avg_complexity:.0f} characters",
                f"- **Variance**: {row.complexity_variance:.0f}",
                f"- **Stability**: {'High' if row.complexity_variance < row.avg_complexity else 'Variable'}",
                "",
                "## Top Entity Types",
                "",
            ]

            if row.top_types_str:
                for item in row.top_types_str.split(", "):
                    parts = item.split(":")
                    if len(parts) == 2:
                        lines.append(f"- **{parts[0]}**: {parts[1]} entities")

            lines.extend([
                "",
                "## Recent Activity Trend",
                "",
                "| Day | Entities |",
                "|-----|----------|",
            ])

            if row.daily_str:
                for item in row.daily_str.split(", ")[:7]:
                    parts = item.split(":")
                    if len(parts) == 2:
                        lines.append(f"| {parts[0]} | {parts[1]} |")

            lines.extend([
                "",
                "## Recommended Deep Dives",
                "",
                "Run these tools for detailed insights:",
                "",
                "1. **`discover_knowledge_graph`** — Map entity relationships",
                "2. **`detect_emergent_patterns`** — Find recurring motifs and anomalies",
                "3. **`analyze_reasoning_chain`** — Trace thought progressions",
                "4. **`detect_temporal_anomalies`** — Find activity irregularities",
                "",
                "## Discovery Methods",
                "",
                "| Method | Purpose | Source |",
                "|--------|---------|--------|",
                "| Knowledge Graph | Relationship mapping | Anthropic Memory MCP |",
                "| Emergent Patterns | Motif + anomaly detection | Matrix Profile |",
                "| Reasoning Chains | Sequential thought tracing | Sequential Thinking MCP |",
                "| Temporal Anomalies | Time series analysis | Microsoft TSA |",
                "",
                "**Framework**: SOVEREIGN Section 24 (Clara Era Legacy)",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"pattern_discovery_dashboard failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((discovery_dashboard_tool, handle_discovery_dashboard))

    return tools
