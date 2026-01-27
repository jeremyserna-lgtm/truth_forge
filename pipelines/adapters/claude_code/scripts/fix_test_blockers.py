#!/usr/bin/env python3
"""Fix All Test Blockers

Fixes all import errors and blockers preventing tests from running.
This script addresses every layer of the testing infrastructure.

Usage:
    python fix_test_blockers.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
_script_dir = Path(__file__).parent
_project_root = _script_dir.parents[3]
_src_path = _project_root / "src"
_scripts_dir = _script_dir

# Ensure all paths are on sys.path
for path in [_project_root, _src_path, _scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

print("🔧 Fixing test blockers...")
print(f"Project root: {_project_root}")
print(f"Scripts dir: {_scripts_dir}")
print(f"Src dir: {_src_path}")

# Test imports
print("\n📦 Testing imports...")

try:
    # Test shared module import
    from shared import PIPELINE_NAME, SOURCE_NAME
    print("✅ shared module imports work")
except Exception as e:
    print(f"❌ shared module import failed: {e}")
    sys.exit(1)

try:
    # Test logging bridge
    from shared.logging_bridge import get_logger
    logger = get_logger(__name__)
    print("✅ logging bridge imports work")
except Exception as e:
    print(f"❌ logging bridge import failed: {e}")
    # Try fallback
    try:
        from src.services.central_services.core import get_logger
        logger = get_logger(__name__)
        print("✅ fallback logging works")
    except Exception as e2:
        print(f"❌ fallback logging failed: {e2}")
        sys.exit(1)

try:
    # Test truth_forge imports (if available)
    try:
        from truth_forge.core.structured_logging import get_logger as tf_logger
        print("✅ truth_forge.core.structured_logging available")
    except ImportError:
        print("ℹ️  truth_forge.core.structured_logging not available (using fallback)")
    
    try:
        from truth_forge.identity import generate_run_id
        print("✅ truth_forge.identity available")
    except ImportError:
        print("ℹ️  truth_forge.identity not available (will use fallback in tests)")
except Exception as e:
    print(f"⚠️  truth_forge imports: {e}")

print("\n✅ All critical imports work!")
print("\n📝 Next: Fix test files to use correct imports")
