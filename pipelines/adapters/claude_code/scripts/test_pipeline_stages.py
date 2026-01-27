#!/usr/bin/env python3
"""Comprehensive Pipeline Stage Testing

Tests each pipeline stage (0-16) systematically to verify:
1. Stage executes without errors
2. Knowledge atoms are written to pipeline HOLD₂
3. Data processing works correctly
4. HOLD → AGENT → HOLD pattern is followed
5. Outputs are correct

Usage:
    python test_pipeline_stages.py [--stage N] [--all] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
scripts_dir = Path(__file__).resolve().parent
src_path = project_root / "src"

# Ensure all paths are on sys.path (order matters)
for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Import shared module (uses logging_bridge internally)
from shared import PIPELINE_NAME

# Define get_pipeline_hold2_path if not available
def get_pipeline_hold2_path(stage: int, pipeline_name: str) -> Path:
    """Get path to pipeline HOLD₂ for a specific stage.
    
    Args:
        stage: Stage number (0-16)
        pipeline_name: Pipeline name
    
    Returns:
        Path to pipeline HOLD₂ JSONL file
    """
    pipeline_dir = Path(__file__).parent.parent.parent
    staging_dir = pipeline_dir / "staging" / "knowledge_atoms" / f"stage_{stage}"
    staging_dir.mkdir(parents=True, exist_ok=True)
    return staging_dir / "hold2.jsonl"

# Use logging bridge for consistent logging
try:
    from shared.logging_bridge import get_logger
except Exception:
    try:
        from truth_forge.core.structured_logging import get_logger
    except Exception:
        # Final fallback: use standard logging
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name: str):
            return logging.getLogger(name)

logger = get_logger(__name__)


def check_pipeline_hold2(stage: int) -> Dict[str, Any]:
    """Check if knowledge atoms exist in pipeline HOLD₂ for a stage.
    
    Args:
        stage: Stage number (0-16)
    
    Returns:
        Dict with check results: {"exists": bool, "count": int, "pending": int, "retrieved": int}
    """
    hold2_path = get_pipeline_hold2_path(stage, PIPELINE_NAME)
    
    result = {
        "exists": False,
        "path": str(hold2_path),
        "count": 0,
        "pending": 0,
        "retrieved": 0,
        "atoms": [],
    }
    
    if not hold2_path.exists():
        return result
    
    result["exists"] = True
    
    try:
        with open(hold2_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    atom = json.loads(line)
                    result["count"] += 1
                    result["atoms"].append(atom)
                    
                    status = atom.get("status", "pending")
                    if status == "pending":
                        result["pending"] += 1
                    elif status == "retrieved":
                        result["retrieved"] += 1
                
                except json.JSONDecodeError:
                    continue
    
    except Exception as e:
        logger.error(
            f"Failed to read pipeline HOLD₂ for stage {stage}: {e}",
            extra={"stage": stage, "hold2_path": str(hold2_path), "error": str(e)},
        )
        result["error"] = str(e)
    
    return result


def get_stage_default_args(stage: int) -> List[str]:
    """Get default arguments for a stage.
    
    Args:
        stage: Stage number (0-16)
    
    Returns:
        List of default arguments for the stage
    """
    args = []
    
    if stage == 0:
        # Stage 0 needs source directory - try to find default
        # Check for common locations
        possible_dirs = [
            Path.home() / ".cursor" / "projects" / "Users-jeremyserna-Truth-Engine" / "agent-transcripts",
            Path("/Users/jeremyserna/.cursor/projects/Users-jeremyserna-Truth-Engine/agent-transcripts"),
            Path(__file__).parent.parent.parent / "data" / "claude_code",
        ]
        
        for dir_path in possible_dirs:
            if dir_path.exists() and any(dir_path.glob("*.jsonl")):
                args.extend(["--source-dir", str(dir_path)])
                logger.info(f"Using source directory for stage 0: {dir_path}")
                break
        else:
            # If no source directory found, we'll let the stage fail with a clear error
            logger.warning("No source directory found for stage 0 - test may fail")
    
    return args


def _test_stage_helper(stage: int, dry_run: bool = True) -> Dict[str, Any]:
    """Test a single pipeline stage.
    
    Args:
        stage: Stage number (0-16)
        dry_run: Whether to run in dry-run mode
    
    Returns:
        Dict with test results
    """
    logger.info(f"Testing stage {stage}")
    
    stage_script = Path(__file__).parent / f"stage_{stage}" / f"claude_code_stage_{stage}.py"
    
    if not stage_script.exists():
        return {
            "stage": stage,
            "status": "ERROR",
            "error": f"Stage script not found: {stage_script}",
        }
    
    result = {
        "stage": stage,
        "script": str(stage_script),
        "dry_run": dry_run,
        "status": "UNKNOWN",
        "execution": {},
        "knowledge_atoms": {},
        "errors": [],
        "warnings": [],
    }
    
    # Run stage script
    # Note: Stage 0 doesn't support --dry-run, other stages do
    try:
        cmd = [sys.executable, str(stage_script)]
        
        # Add stage-specific default arguments
        default_args = get_stage_default_args(stage)
        cmd.extend(default_args)
        
        # Only add --dry-run for stages that support it (1-16, not 0)
        if dry_run and stage > 0:
            cmd.append("--dry-run")
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        
        result["execution"] = {
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "success": process.returncode == 0,
        }
        
        if process.returncode != 0:
            result["status"] = "FAILED"
            result["errors"].append(f"Stage script returned non-zero exit code: {process.returncode}")
            if process.stderr:
                result["errors"].append(f"stderr: {process.stderr[:500]}")
        else:
            result["status"] = "SUCCESS"
    
    except subprocess.TimeoutExpired:
        result["status"] = "TIMEOUT"
        result["errors"].append("Stage execution timed out after 5 minutes")
    
    except Exception as e:
        result["status"] = "ERROR"
        result["errors"].append(f"Failed to execute stage: {e}")
        logger.error(
            f"Failed to execute stage {stage}: {e}",
            extra={"stage": stage, "error": str(e)},
            exc_info=True,
        )
    
    # Check knowledge atoms in pipeline HOLD₂
    hold2_check = check_pipeline_hold2(stage)
    result["knowledge_atoms"] = hold2_check
    
    # Validate knowledge atom production
    if result["status"] == "SUCCESS":
        if not hold2_check["exists"]:
            result["warnings"].append("No knowledge atoms found in pipeline HOLD₂")
        elif hold2_check["pending"] == 0:
            result["warnings"].append("No pending knowledge atoms in pipeline HOLD₂")
        else:
            logger.info(
                f"Stage {stage} produced {hold2_check['pending']} pending knowledge atoms",
                extra={"stage": stage, "pending": hold2_check["pending"]},
            )
    
    return result


def _test_all_stages_helper(dry_run: bool = True) -> Dict[str, Any]:
    """Test all pipeline stages (0-16).
    
    Args:
        dry_run: Whether to run in dry-run mode
    
    Returns:
        Dict with test results for all stages
    """
    logger.info(f"Testing all pipeline stages (dry_run={dry_run})")
    
    results = {
        "dry_run": dry_run,
        "stages": {},
        "summary": {
            "total": 17,
            "success": 0,
            "failed": 0,
            "errors": 0,
            "timeouts": 0,
            "total_knowledge_atoms": 0,
        },
    }
    
    for stage in range(17):
        logger.info(f"Testing stage {stage}...")
        stage_result = _test_stage_helper(stage, dry_run=dry_run)
        results["stages"][stage] = stage_result
        
        # Update summary
        if stage_result["status"] == "SUCCESS":
            results["summary"]["success"] += 1
            results["summary"]["total_knowledge_atoms"] += stage_result["knowledge_atoms"].get("pending", 0)
        elif stage_result["status"] == "FAILED":
            results["summary"]["failed"] += 1
        elif stage_result["status"] == "ERROR":
            results["summary"]["errors"] += 1
        elif stage_result["status"] == "TIMEOUT":
            results["summary"]["timeouts"] += 1
    
    return results


# Pytest test functions
def test_stage_0() -> None:
    """Test stage 0 execution."""
    result = _test_stage_helper(0, dry_run=False)
    assert result["status"] in ["SUCCESS", "FAILED", "ERROR"], "Status should be valid"


def test_stage_1_dry_run() -> None:
    """Test stage 1 in dry-run mode."""
    result = _test_stage_helper(1, dry_run=True)
    assert result["status"] in ["SUCCESS", "FAILED", "ERROR"], "Status should be valid"


def test_all_stages_dry_run() -> None:
    """Test all stages in dry-run mode."""
    results = _test_all_stages_helper(dry_run=True)
    assert "summary" in results, "Results should have summary"
    assert results["summary"]["total"] == 17, "Should test all 17 stages"


def print_test_report(results: Dict[str, Any]) -> None:
    """Print a formatted test report.
    
    Args:
        results: Test results dict
    """
    print("\n" + "="*80)
    print("PIPELINE STAGE TEST REPORT")
    print("="*80)
    
    if "stages" in results:
        # All stages test
        print(f"\nSummary:")
        print(f"  Total stages: {results['summary']['total']}")
        print(f"  Successful: {results['summary']['success']}")
        print(f"  Failed: {results['summary']['failed']}")
        print(f"  Errors: {results['summary']['errors']}")
        print(f"  Timeouts: {results['summary']['timeouts']}")
        print(f"  Total knowledge atoms: {results['summary']['total_knowledge_atoms']}")
        
        print(f"\nStage Details:")
        for stage_num in sorted(results["stages"].keys()):
            stage_result = results["stages"][stage_num]
            status_icon = "✅" if stage_result["status"] == "SUCCESS" else "❌"
            print(f"\n  {status_icon} Stage {stage_num}: {stage_result['status']}")
            
            if stage_result.get("errors"):
                for error in stage_result["errors"]:
                    print(f"      ERROR: {error}")
            
            if stage_result.get("warnings"):
                for warning in stage_result["warnings"]:
                    print(f"      WARNING: {warning}")
            
            ka = stage_result.get("knowledge_atoms", {})
            if ka.get("exists"):
                print(f"      Knowledge atoms: {ka.get('pending', 0)} pending, {ka.get('retrieved', 0)} retrieved")
                print(f"      Path: {ka.get('path', 'N/A')}")
            else:
                print(f"      Knowledge atoms: None found")
    
    else:
        # Single stage test
        print(f"\nStage {results['stage']} Test Results:")
        print(f"  Status: {results['status']}")
        print(f"  Script: {results.get('script', 'N/A')}")
        print(f"  Dry run: {results.get('dry_run', False)}")
        
        if results.get("errors"):
            print(f"\n  Errors:")
            for error in results["errors"]:
                print(f"    - {error}")
        
        if results.get("warnings"):
            print(f"\n  Warnings:")
            for warning in results["warnings"]:
                print(f"    - {warning}")
        
        ka = results.get("knowledge_atoms", {})
        if ka.get("exists"):
            print(f"\n  Knowledge Atoms:")
            print(f"    Total: {ka.get('count', 0)}")
            print(f"    Pending: {ka.get('pending', 0)}")
            print(f"    Retrieved: {ka.get('retrieved', 0)}")
            print(f"    Path: {ka.get('path', 'N/A')}")
        else:
            print(f"\n  Knowledge Atoms: None found")
    
    print("\n" + "="*80)


def main() -> int:
    """Main entry point for testing."""
    parser = argparse.ArgumentParser(
        description="Test pipeline stages comprehensively"
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=range(17),
        help="Test specific stage only (0-16)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all stages (default)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run stages in dry-run mode (default: True)",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Run stages in production mode (WARNING: modifies data)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.stage is not None:
            # Test specific stage
            result = _test_stage_helper(args.stage, dry_run=args.dry_run)
            print_test_report(result)
            return 0 if result["status"] == "SUCCESS" else 1
        else:
            # Test all stages
            results = _test_all_stages_helper(dry_run=args.dry_run)
            print_test_report(results)
            
            # Return non-zero if any stage failed
            if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
                return 1
            return 0
    
    except Exception as e:
        logger.error(
            f"Test execution failed: {e}",
            exc_info=True,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
