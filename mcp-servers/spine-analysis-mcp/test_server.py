#!/usr/bin/env python3
"""Quick test script for spine-analysis-mcp server.

Tests basic functionality without full MCP client.
"""

import sys
from spine_analysis_mcp.config import get_bigquery_client
from spine_analysis_mcp.tools import query_tools, source_tools

def test_bigquery_connection():
    """Test BigQuery connection."""
    try:
        client = get_bigquery_client()
        print("✅ BigQuery client created successfully")
        return True
    except Exception as e:
        print(f"❌ BigQuery connection failed: {e}")
        return False

def test_tools_registration():
    """Test that tools can be registered."""
    try:
        query_tools_list = query_tools.get_tools()
        source_tools_list = source_tools.get_tools()
        
        print(f"✅ Query tools: {len(query_tools_list)} tools")
        print(f"✅ Source tools: {len(source_tools_list)} tools")
        
        total = len(query_tools_list) + len(source_tools_list)
        print(f"✅ Total tools tested: {total}")
        return True
    except Exception as e:
        print(f"❌ Tool registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sample_query():
    """Test a sample query."""
    try:
        tools = query_tools.get_tools()
        if not tools:
            print("⚠️  No query tools available")
            return False
        
        # Get the first tool handler
        tool, handler = tools[0]
        print(f"✅ Testing tool: {tool.name}")
        
        # Test with minimal arguments
        result = handler({"limit": 5})
        print(f"✅ Query executed successfully")
        print(f"   Result length: {len(result)} characters")
        return True
    except Exception as e:
        print(f"❌ Sample query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Spine Analysis MCP Server\n")
    print("=" * 50)
    
    tests = [
        ("BigQuery Connection", test_bigquery_connection),
        ("Tool Registration", test_tools_registration),
        ("Sample Query", test_sample_query),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} raised exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("\nTest Summary:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(result for _, result in results)
    sys.exit(0 if all_passed else 1)
