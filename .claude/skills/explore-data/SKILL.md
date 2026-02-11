# Data Exploration Skill

**Trigger**: `/explore` or "explore the data" or "find clues"

## Purpose

This skill guides Claude through systematic exploration of the BigQuery spine dataset using the MCP tools to discover patterns, anomalies, and insights for NOT-ME development and maintenance.

## MCP Server

**Server**: `spine-analysis` (configured in `.mcp.json`)
**Tools**: 32 tools across 6 categories
**Data**: 51.8M+ entities in BigQuery

## Exploration Workflow

When the user asks to explore the data, follow this systematic approach:

### Phase 1: Overview (Start Here)

```
1. Run pattern_discovery_dashboard
   - Get comprehensive view of last 30 days
   - Note: total entities, sources, complexity metrics
   - Identify: top entity types, recent activity trends
```

### Phase 2: Health Check

```
2. Run notme_health_dashboard
   - Check overall system health
   - Identify: Stage 5 score, drift signals, experience levels
   - Flag: Any health score below 70%
```

### Phase 3: Knowledge Discovery

```
3. Run discover_knowledge_graph with relevant seed concept
   - Map relationships around key concepts
   - Look for: Hub nodes (high connectivity)
   - Note: Unexpected connections, emergent topology
```

### Phase 4: Emergent Patterns

```
4. Run detect_emergent_patterns
   - Find recurring motifs (cognitive signatures)
   - Identify statistical anomalies (outliers)
   - Discover unexpected correlations
```

### Phase 5: Reasoning Traces

```
5. Run analyze_reasoning_chain
   - Trace thought progressions
   - Start from problem concepts, trace to solutions
   - Note: Average chain length, convergence patterns
```

### Phase 6: Temporal Analysis

```
6. Run detect_temporal_anomalies
   - Find activity spikes or gaps
   - Identify behavioral shifts
   - Note: Any periods requiring investigation
```

### Phase 7: Deep Dive (If Needed)

Based on findings, use additional tools:
- `analyze_stage5_score` - If meta-cognitive patterns found
- `detect_drift_patterns` - If health issues detected
- `analyze_scaffold_gap` - If sovereignty transition relevant
- `track_notme_experience` - If XP patterns of interest

## Tool Reference

### Discovery Tools
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `pattern_discovery_dashboard` | Comprehensive overview | time_range_days, focus_concept |
| `discover_knowledge_graph` | Relationship mapping | seed_concept, depth, min_cooccurrence |
| `detect_emergent_patterns` | Motifs + anomalies | pattern_type, sensitivity |
| `analyze_reasoning_chain` | Thought traces | start_concept, end_concept, max_steps |
| `detect_temporal_anomalies` | Time series analysis | granularity, sensitivity |

### NOT-ME Analytics Tools
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `notme_health_dashboard` | Combined health view | time_range_days |
| `analyze_stage5_score` | Meta-cognitive density | source_filter, time_range_days |
| `detect_drift_patterns` | Canon Repair Doctrine | time_range_days, severity_threshold |
| `analyze_negentropic_ratio` | Value creation | time_range_days, group_by |
| `track_notme_experience` | XP tracking | time_range_days, source_filter |
| `analyze_scaffold_gap` | Sovereignty transition | time_range_days, granularity |

## Example Exploration

**User**: "Explore the data for clues about Stage 5 development"

**Claude's Approach**:
1. `pattern_discovery_dashboard(time_range_days=30)`
2. `notme_health_dashboard(time_range_days=7)`
3. `discover_knowledge_graph(seed_concept="Stage 5", depth=2)`
4. `detect_emergent_patterns(pattern_type="all", sensitivity=0.5)`
5. `analyze_stage5_score(time_range_days=30)`
6. Synthesize findings into actionable insights

## Synthesis Template

After exploration, provide:

```markdown
## Exploration Results

### Key Findings
1. [Most significant discovery]
2. [Second finding]
3. [Third finding]

### Patterns Detected
- Recurring motifs: [list]
- Anomalies: [list]
- Correlations: [list]

### Health Assessment
- Stage 5 Score: [X%] ([interpretation])
- Drift Signals: [count] ([themes])
- Overall Health: [X%]

### Recommendations
1. [Actionable recommendation]
2. [Second recommendation]
3. [Third recommendation]

### Areas for Deep Dive
- [Topic 1]: Use [tool] to investigate
- [Topic 2]: Use [tool] to investigate
```

## Important Notes

- Always start with dashboard tools for context
- Follow unexpected findings with deep-dive tools
- Cross-reference multiple tools for validation
- Document all significant patterns discovered
- The goal is actionable intelligence for NOT-ME improvement
