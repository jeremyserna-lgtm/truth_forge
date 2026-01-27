#!/usr/bin/env python3
"""Example queries demonstrating spine-analysis-mcp server capabilities.

These examples show how to use the tools programmatically.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spine_analysis_mcp.tools import (
    concept_tools,
    cross_level_tools,
    pattern_tools,
    query_tools,
    relationship_tools,
    semantic_tools,
    source_tools,
    spine_level_tools,
    temporal_tools,
    trend_tools,
)


def example_1_track_all_sources():
    """Example: Track data from all 5 sources."""
    print("\n" + "=" * 60)
    print("Example 1: Track All Data Sources")
    print("=" * 60)
    
    tools = source_tools.get_tools()
    track_tool = None
    for tool, handler in tools:
        if tool.name == "track_source_data":
            track_tool = handler
            break
    
    if track_tool:
        result = track_tool({
            "sources": ["claude_code", "claude_web", "gemini_web", "codex", "cursor"],
            "time_range": "last_30_days",
            "metrics": ["volume", "entities", "domains"]
        })
        print(result)
    else:
        print("❌ track_source_data tool not found")


def example_2_explore_concept():
    """Example: Explore a specific concept."""
    print("\n" + "=" * 60)
    print("Example 2: Explore Concept - 'cognitive isomorphism'")
    print("=" * 60)
    
    tools = concept_tools.get_tools()
    explore_tool = None
    for tool, handler in tools:
        if tool.name == "explore_concept":
            explore_tool = handler
            break
    
    if explore_tool:
        result = explore_tool({
            "concept": "cognitive isomorphism",
            "limit": 20
        })
        print(result)
    else:
        print("❌ explore_concept tool not found")


def example_3_analyze_temporal_trends():
    """Example: Analyze temporal trends."""
    print("\n" + "=" * 60)
    print("Example 3: Analyze Temporal Trends")
    print("=" * 60)
    
    tools = trend_tools.get_tools()
    trend_tool = None
    for tool, handler in tools:
        if tool.name == "analyze_temporal_trends":
            trend_tool = handler
            break
    
    if trend_tool:
        result = trend_tool({
            "metric": "entity_creation",
            "time_range": "last_90_days",
            "granularity": "daily",
            "group_by": "source_system"
        })
        print(result)
    else:
        print("❌ analyze_temporal_trends tool not found")


def example_4_analyze_spine_level():
    """Example: Analyze a specific spine level."""
    print("\n" + "=" * 60)
    print("Example 4: Analyze Spine Level 8 (Document Level)")
    print("=" * 60)
    
    tools = spine_level_tools.get_tools()
    level_tool = None
    for tool, handler in tools:
        if tool.name == "analyze_spine_level":
            level_tool = handler
            break
    
    if level_tool:
        result = level_tool({
            "level": 8
        })
        print(result)
    else:
        print("❌ analyze_spine_level tool not found")


def example_5_find_relationships():
    """Example: Find entity relationships."""
    print("\n" + "=" * 60)
    print("Example 5: Find Entity Relationships")
    print("=" * 60)
    
    tools = relationship_tools.get_tools()
    rel_tool = None
    for tool, handler in tools:
        if tool.name == "find_entity_relationships":
            rel_tool = handler
            break
    
    if rel_tool:
        # First, get an entity ID from a query
        query_tools_list = query_tools.get_tools()
        query_tool = None
        for tool, handler in query_tools_list:
            if tool.name == "query_entities":
                query_tool = handler
                break
        
        if query_tool:
            # Get a sample entity
            sample_result = query_tool({"limit": 1})
            print("Sample entity query result:")
            print(sample_result[:500] + "...")
            print("\nNote: To find relationships, provide a specific entity_id")
        else:
            print("❌ query_entities tool not found")
    else:
        print("❌ find_entity_relationships tool not found")


def example_6_analyze_patterns():
    """Example: Analyze patterns."""
    print("\n" + "=" * 60)
    print("Example 6: Detect Patterns")
    print("=" * 60)
    
    tools = pattern_tools.get_tools()
    pattern_tool = None
    for tool, handler in tools:
        if tool.name == "detect_patterns":
            pattern_tool = handler
            break
    
    if pattern_tool:
        result = pattern_tool({
            "pattern_type": "frequency",
            "min_frequency": 10
        })
        print(result)
    else:
        print("❌ detect_patterns tool not found")


def example_7_cross_level_analysis():
    """Example: Cross-level analysis."""
    print("\n" + "=" * 60)
    print("Example 7: Cross-Level Distribution")
    print("=" * 60)
    
    tools = cross_level_tools.get_tools()
    cross_tool = None
    for tool, handler in tools:
        if tool.name == "analyze_cross_level_distribution":
            cross_tool = handler
            break
    
    if cross_tool:
        result = cross_tool({
            "group_by": "source_system"
        })
        print(result)
    else:
        print("❌ analyze_cross_level_distribution tool not found")


def example_8_temporal_cycles():
    """Example: Analyze activity cycles."""
    print("\n" + "=" * 60)
    print("Example 8: Analyze Activity Cycles (Day of Week)")
    print("=" * 60)
    
    tools = temporal_tools.get_tools()
    cycle_tool = None
    for tool, handler in tools:
        if tool.name == "analyze_activity_cycles":
            cycle_tool = handler
            break
    
    if cycle_tool:
        result = cycle_tool({
            "cycle_type": "day_of_week",
            "time_range": "last_90_days"
        })
        print(result)
    else:
        print("❌ analyze_activity_cycles tool not found")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Spine Analysis MCP Server - Example Queries")
    print("=" * 60)
    print("\nThese examples demonstrate the capabilities of the server.")
    print("Note: Some examples require actual BigQuery data to work properly.")
    print("\nRunning examples...")
    
    examples = [
        ("Track All Sources", example_1_track_all_sources),
        ("Explore Concept", example_2_explore_concept),
        ("Temporal Trends", example_3_analyze_temporal_trends),
        ("Spine Level Analysis", example_4_analyze_spine_level),
        ("Find Relationships", example_5_find_relationships),
        ("Detect Patterns", example_6_analyze_patterns),
        ("Cross-Level Analysis", example_7_cross_level_analysis),
        ("Activity Cycles", example_8_temporal_cycles),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
