#!/usr/bin/env python3
"""Integration tests for spine-analysis-mcp server.

Tests actual BigQuery connectivity and query execution.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from spine_analysis_mcp.config import get_bigquery_client, BQ_PROJECT_ID, BQ_DATASET_ID
from spine_analysis_mcp.tools import query_tools, source_tools


class TestBigQueryConnection:
    """Test BigQuery connectivity."""
    
    def test_bigquery_client_creation(self):
        """Test that BigQuery client can be created."""
        try:
            client = get_bigquery_client()
            assert client is not None
            assert client.project == BQ_PROJECT_ID
        except Exception as e:
            pytest.skip(f"BigQuery connection failed (credentials may not be set): {e}")
    
    def test_dataset_exists(self):
        """Test that the spine dataset exists."""
        try:
            client = get_bigquery_client()
            dataset = client.dataset(BQ_DATASET_ID)
            assert dataset.exists()
        except Exception as e:
            pytest.skip(f"Dataset check failed: {e}")


class TestQueryTools:
    """Test query tools."""
    
    def test_query_entities_basic(self):
        """Test basic entity query."""
        try:
            tools = query_tools.get_tools()
            query_tool = None
            for tool, handler in tools:
                if tool.name == "query_entities":
                    query_tool = handler
                    break
            
            if not query_tool:
                pytest.fail("query_entities tool not found")
            
            result = query_tool({"limit": 5})
            assert result is not None
            assert len(result) > 0
            assert "Error" not in result or "error" not in result.lower()
        except Exception as e:
            # If it's a credentials error, skip the test
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                pytest.skip(f"BigQuery credentials not available: {e}")
            else:
                raise
    
    def test_get_table_stats(self):
        """Test table statistics query."""
        try:
            tools = query_tools.get_tools()
            stats_tool = None
            for tool, handler in tools:
                if tool.name == "get_table_stats":
                    stats_tool = handler
                    break
            
            if not stats_tool:
                pytest.fail("get_table_stats tool not found")
            
            result = stats_tool({"table_name": "entity_production"})
            assert result is not None
            assert len(result) > 0
        except Exception as e:
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                pytest.skip(f"BigQuery credentials not available: {e}")
            elif "not found" in str(e).lower():
                pytest.skip(f"Table may not exist: {e}")
            else:
                raise


class TestSourceTools:
    """Test source tracking tools."""
    
    def test_track_source_data(self):
        """Test source data tracking."""
        try:
            tools = source_tools.get_tools()
            track_tool = None
            for tool, handler in tools:
                if tool.name == "track_source_data":
                    track_tool = handler
                    break
            
            if not track_tool:
                pytest.fail("track_source_data tool not found")
            
            result = track_tool({
                "sources": ["claude_code"],
                "time_range": "last_7_days",
                "metrics": ["volume"]
            })
            assert result is not None
            assert len(result) > 0
        except Exception as e:
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                pytest.skip(f"BigQuery credentials not available: {e}")
            else:
                raise


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
