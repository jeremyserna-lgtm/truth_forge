import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to the path so that imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock duckdb to prevent import errors during testing
# This is a blocker that prevents tests from running
try:
    import duckdb
except ImportError:
    # Create a mock duckdb module if import fails
    duckdb_mock = Mock()
    sys.modules['duckdb'] = duckdb_mock
    sys.modules['_duckdb'] = Mock()
    sys.modules['_duckdb._sqltypes'] = Mock()
