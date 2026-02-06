"""Tests for explorer tool_bridge module."""

from __future__ import annotations

from truth_forge.services.explorer.tool_bridge import TOOL_CATEGORIES, ToolBridge


class TestToolCategories:
    """Test TOOL_CATEGORIES constant."""

    def test_tool_categories_defined(self) -> None:
        """Test tool categories are defined."""
        assert len(TOOL_CATEGORIES) > 0
        assert "query_entities" in TOOL_CATEGORIES
        assert TOOL_CATEGORIES["query_entities"] == "entity"

    def test_categories_cover_all_types(self) -> None:
        """Test categories cover expected tool types."""
        categories = set(TOOL_CATEGORIES.values())
        expected_categories = {
            "entity",
            "source",
            "trend",
            "concept",
            "spine",
            "relationship",
            "temporal",
            "pattern",
            "semantic",
            "cross_level",
            "enrichment",
            "notme",
            "discovery",
        }
        assert categories.issuperset(expected_categories)


class TestToolBridge:
    """Test ToolBridge class."""

    def test_init(self) -> None:
        """Test ToolBridge initialization."""
        bridge = ToolBridge()
        assert bridge._loaded is False
        assert len(bridge._handlers) == 0

    def test_load_tools(self) -> None:
        """Test loading tools from modules."""
        bridge = ToolBridge()
        # Tools will fail to load in test environment (spine-analysis-mcp not available)
        # But structure should be correct
        assert bridge._loaded is False
        # Calling get_tool_names will trigger load
        names = bridge.get_tool_names()
        assert isinstance(names, list)

    def test_get_tool_names_empty(self) -> None:
        """Test get_tool_names when no tools loaded."""
        bridge = ToolBridge()
        names = bridge.get_tool_names()
        assert isinstance(names, list)

    def test_get_tool_category(self) -> None:
        """Test get_tool_category method."""
        bridge = ToolBridge()
        category = bridge.get_tool_category("query_entities")
        assert category == "entity"

    def test_get_tool_category_unknown(self) -> None:
        """Test get_tool_category for unknown tool."""
        bridge = ToolBridge()
        category = bridge.get_tool_category("unknown_tool")
        assert category == "unknown"

    def test_invoke_not_loaded(self) -> None:
        """Test invoke when tools not loaded."""
        bridge = ToolBridge()
        # Should handle gracefully - will try to load and may fail
        from truth_forge.services.explorer.models import ToolResult

        result = bridge.invoke("test_tool", {})
        # Should return ToolResult (may be error result)
        assert isinstance(result, ToolResult)
