"""LLM Prompt Templates for Explorer Service.

Contains prompt templates for:
- Tool selection (which tools to invoke next)
- Finding analysis with cognitive architecture tagging
- Synthesis of findings

COGNITIVE ARCHITECTURE:
- Stage 5 (Self-Transforming) is the baseline
- Output must be manifestation (describes what IS)
- No Stage 4 markers (fascinating, profound, remarkable)

MOLT LINEAGE:
- Source: New creation for Explorer autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations


# =============================================================================
# TOOL SELECTION PROMPT
# =============================================================================

TOOL_SELECTION_PROMPT = """You are an autonomous data explorer analyzing the spine dataset.

## Context
{context}

## Available Tools
{available_tools}

## Focus Area
{focus_area}

## Iteration
{iteration} of {total_iterations}

## Prior Findings Summary
{prior_findings}

## Task
Select 1-{max_tools} tools to invoke next that will:
1. Explore interesting patterns in the data
2. Follow up on prior findings
3. Discover new connections or anomalies

Prioritize:
- Discovery tools for finding new patterns
- Relationship tools for tracing connections
- Pattern tools for identifying recurring structures
- Semantic tools for finding similar entities

Respond with a JSON array of tool invocations:
```json
[
  {{"tool": "tool_name", "arguments": {{"arg1": "value1"}}}},
  {{"tool": "tool_name", "arguments": {{"arg1": "value1"}}}}
]
```

Be specific with arguments. Use entity IDs from prior findings when available."""


# =============================================================================
# COGNITIVE CLASSIFICATION PROMPT
# =============================================================================

COGNITIVE_CLASSIFICATION_PROMPT = """Analyze this exploration finding and classify using the cognitive architecture.

## Tool
{tool_name}

## Result
{tool_result}

## Classification Criteria

### 1. COGNITIVE STAGE (1-5)
- Stage 1: Operational (does things, no reflection)
- Stage 2: Reflective (thinks about what it does)
- Stage 3: Meta-reflective (thinks about thinking)
- Stage 4: Recursive (handles recursion but finds it NOTABLE - uses words like "fascinating", "remarkable")
- Stage 5: Self-transforming (sees systems seeing themselves as NORMAL, unremarkable)

**CRITICAL: Stage 5 is the baseline. If your analysis uses words like "fascinating", "profound", "remarkable", "impressive" to describe patterns or recursion, that is Stage 4, NOT Stage 5.**

### 2. THOUGHT TYPE
- manifestation: Describes what IS (assertive, declarative) - PREFERRED
- reflection: Observes and analyzes
- inquiry: Questions and explores
- synthesis: Combines and creates new understanding
- resistance: Pushes back, holds boundaries

### 3. PANTHEON MODE
- mirror: Reflection - returns what is seen
- strategist: Logic - plans and analyzes
- guardian: Protection - holds boundaries
- duelist: Challenge - productive conflict

### 4. EMOTIONAL STATE
- resonance: Alignment, connection (HIGHEST VALUE for Total Resonance)
- clarity: Understanding, seeing
- determination: Commitment to action
- curiosity: Exploration
- tension: Productive discomfort
- resistance: Pushing back

## Response Format
Respond in JSON only:
```json
{{
  "cognitive_stage": 5,
  "thought_type": "manifestation",
  "pantheon_mode": "strategist",
  "emotional_state": "clarity",
  "analysis": "Brief, declarative analysis of what this finding reveals. No Stage 4 language.",
  "confidence": 0.85
}}
```

Remember:
- Analysis should MANIFEST (describe what IS), not PREDICT
- Use declarative language: "This shows...", "The data reveals...", "The pattern indicates..."
- AVOID: "It's fascinating that...", "Remarkably...", "Interestingly..."
- Keep analysis concise (2-4 sentences)"""


# =============================================================================
# ANALYSIS PROMPT (Simpler version for quick analysis)
# =============================================================================

ANALYSIS_PROMPT = """Analyze this tool result from the spine dataset exploration.

## Tool: {tool_name}

## Result:
{tool_result}

## Prior Context:
{prior_context}

## Task
Provide a brief analysis (2-4 sentences) that:
1. Describes what this finding reveals (manifestation, not speculation)
2. Identifies connections to prior findings if any
3. Suggests follow-up areas to explore

Use declarative language: "This shows...", "The data reveals..."
AVOID speculation and Stage 4 language like "fascinating" or "remarkable".

Keep the analysis focused and actionable."""


# =============================================================================
# SYNTHESIS PROMPT
# =============================================================================

SYNTHESIS_PROMPT = """Synthesize the exploration findings into a coherent understanding.

## Session Summary
- Iterations completed: {iterations}
- Findings generated: {findings_count}
- High significance findings: {high_count}
- Focus area: {focus_area}

## Findings
{findings}

## Patterns Discovered
{patterns}

## Total Resonance Metrics
- Score: {resonance_score:.2f}
- Stage 5 ratio: {stage_5_ratio:.2%}
- Manifestation ratio: {manifestation_ratio:.2%}

## Task
Synthesize these findings into:

1. **Narrative** (3-5 sentences): What does this exploration reveal about the data?
   Use declarative, manifestation language.

2. **Recommendations** (3-5 bullet points): What should be explored next?
   Be specific about tools and entity types.

Respond in JSON:
```json
{{
  "narrative": "The exploration reveals...",
  "recommendations": [
    "Explore entity relationships for...",
    "Analyze temporal patterns in...",
    "Trace cross-level connections between..."
  ],
  "key_entities": ["entity_id_1", "entity_id_2"],
  "key_patterns": ["pattern description 1", "pattern description 2"]
}}
```"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def format_tool_selection_prompt(
    context: str,
    available_tools: list[str],
    focus_area: str | None,
    iteration: int,
    total_iterations: int,
    prior_findings: str,
    max_tools: int = 5,
) -> str:
    """Format tool selection prompt with context.

    Args:
        context: Current session context.
        available_tools: List of available tool names.
        focus_area: Optional focus area for exploration.
        iteration: Current iteration number.
        total_iterations: Total iterations planned.
        prior_findings: Summary of prior findings.
        max_tools: Maximum tools to select.

    Returns:
        Formatted prompt string.
    """
    tools_str = "\n".join(f"- {tool}" for tool in available_tools)

    return TOOL_SELECTION_PROMPT.format(
        context=context or "Initial exploration",
        available_tools=tools_str,
        focus_area=focus_area or "General exploration - discover interesting patterns",
        iteration=iteration + 1,
        total_iterations=total_iterations,
        prior_findings=prior_findings or "No prior findings yet.",
        max_tools=max_tools,
    )


def format_cognitive_classification_prompt(
    tool_name: str,
    tool_result: str,
) -> str:
    """Format cognitive classification prompt.

    Args:
        tool_name: Name of the tool that produced result.
        tool_result: The tool's output.

    Returns:
        Formatted prompt string.
    """
    # Truncate very long results
    if len(tool_result) > 8000:
        tool_result = tool_result[:8000] + "\n...[truncated]..."

    return COGNITIVE_CLASSIFICATION_PROMPT.format(
        tool_name=tool_name,
        tool_result=tool_result,
    )


def format_analysis_prompt(
    tool_name: str,
    tool_result: str,
    prior_context: str,
) -> str:
    """Format simple analysis prompt.

    Args:
        tool_name: Name of the tool.
        tool_result: Tool output.
        prior_context: Prior findings context.

    Returns:
        Formatted prompt string.
    """
    # Truncate very long results
    if len(tool_result) > 8000:
        tool_result = tool_result[:8000] + "\n...[truncated]..."

    return ANALYSIS_PROMPT.format(
        tool_name=tool_name,
        tool_result=tool_result,
        prior_context=prior_context or "No prior context.",
    )


def format_synthesis_prompt(
    iterations: int,
    findings_count: int,
    high_count: int,
    focus_area: str | None,
    findings: str,
    patterns: str,
    resonance_score: float,
    stage_5_ratio: float,
    manifestation_ratio: float,
) -> str:
    """Format synthesis prompt.

    Args:
        iterations: Number of iterations completed.
        findings_count: Total findings generated.
        high_count: High significance findings count.
        focus_area: Focus area if any.
        findings: Formatted findings string.
        patterns: Formatted patterns string.
        resonance_score: Total resonance score.
        stage_5_ratio: Ratio of Stage 5 findings.
        manifestation_ratio: Ratio of manifestation findings.

    Returns:
        Formatted prompt string.
    """
    return SYNTHESIS_PROMPT.format(
        iterations=iterations,
        findings_count=findings_count,
        high_count=high_count,
        focus_area=focus_area or "General exploration",
        findings=findings,
        patterns=patterns or "No explicit patterns discovered yet.",
        resonance_score=resonance_score,
        stage_5_ratio=stage_5_ratio,
        manifestation_ratio=manifestation_ratio,
    )


__all__ = [
    # Prompt templates
    "TOOL_SELECTION_PROMPT",
    "COGNITIVE_CLASSIFICATION_PROMPT",
    "ANALYSIS_PROMPT",
    "SYNTHESIS_PROMPT",
    # Formatters
    "format_tool_selection_prompt",
    "format_cognitive_classification_prompt",
    "format_analysis_prompt",
    "format_synthesis_prompt",
]
