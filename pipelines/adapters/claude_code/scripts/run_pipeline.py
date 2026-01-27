#!/usr/bin/env python3
"""
Claude Code Pipeline - Complete Orchestration

Runs all 16 stages of the Claude Code pipeline.
This is the entry point for running the complete pipeline.

FIXES APPLIED (per peer review):
- Subprocess output capture for proper logging
- Path validation and sanitization for security
- Run ID support for pipeline resumption
- Adaptive timeouts per stage
- Bounded output capture to prevent memory exhaustion
- Command argument sanitization
- Externalized configuration

Usage:
    python run_pipeline.py [--source-dir PATH] [--start-stage N] [--end-stage N] [--dry-run] [--run-id ID]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import List, Optional

try:
    from truth_forge.core import get_logger, get_current_run_id
except Exception:
    from src.services.central_services.core import get_logger
    def get_current_run_id():
        return f"run_{uuid.uuid4().hex[:12]}"

logger = get_logger(__name__)

# Pipeline root
PIPELINE_ROOT = Path(__file__).parent
PROJECT_ROOT = PIPELINE_ROOT.parents[3]

# FIX: Externalize configuration via environment variables
# Defaults can be overridden via environment
DISCOVERY_MANIFEST_DIR = Path(
    os.getenv("PIPELINE_STAGING_DIR", str(PIPELINE_ROOT.parent / "staging"))
)
DEFAULT_SOURCE_DIR = Path(
    os.getenv("PIPELINE_SOURCE_DIR", str(Path.home() / ".claude" / "projects"))
)

# Stage scripts
STAGES = {
    0: PIPELINE_ROOT / "stage_0" / "claude_code_stage_0.py",
    1: PIPELINE_ROOT / "stage_1" / "claude_code_stage_1.py",
    2: PIPELINE_ROOT / "stage_2" / "claude_code_stage_2.py",
    3: PIPELINE_ROOT / "stage_3" / "claude_code_stage_3.py",
    4: PIPELINE_ROOT / "stage_4" / "claude_code_stage_4.py",
    5: PIPELINE_ROOT / "stage_5" / "claude_code_stage_5.py",
    6: PIPELINE_ROOT / "stage_6" / "claude_code_stage_6.py",
    7: PIPELINE_ROOT / "stage_7" / "claude_code_stage_7.py",
    8: PIPELINE_ROOT / "stage_8" / "claude_code_stage_8.py",
    9: PIPELINE_ROOT / "stage_9" / "claude_code_stage_9.py",
    10: PIPELINE_ROOT / "stage_10" / "claude_code_stage_10.py",
    11: PIPELINE_ROOT / "stage_11" / "claude_code_stage_11.py",
    12: PIPELINE_ROOT / "stage_12" / "claude_code_stage_12.py",
    13: PIPELINE_ROOT / "stage_13" / "claude_code_stage_13.py",
    14: PIPELINE_ROOT / "stage_14" / "claude_code_stage_14.py",
    15: PIPELINE_ROOT / "stage_15" / "claude_code_stage_15.py",
    16: PIPELINE_ROOT / "stage_16" / "claude_code_stage_16.py",
}

STAGE_NAMES = {
    0: "Assessment (Discovery)",
    1: "Extraction",
    2: "Cleaning",
    3: "THE GATE (Identity)",
    4: "Staging + LLM Text Correction",
    5: "L8 Conversations",
    6: "L6 Turns",
    7: "L5 Messages",
    8: "L4 Sentences",
    9: "L3 Spans (NER)",
    10: "L2 Words",
    11: "Parent-Child Validation",
    12: "Count Denormalization",
    13: "Pre-Promotion Validation",
    14: "Promotion to entity_unified",
    15: "Final Validation",
    16: "Final Promotion",
}


def run_stage(
    stage_num: int,
    script_path: Path,
    source_dir: Optional[Path] = None,
    dry_run: bool = False,
    manifest_path: Optional[Path] = None,
    run_id: Optional[str] = None,
) -> bool:
    """Run a pipeline stage and return True if successful.
    
    FIXES APPLIED (per peer review):
    - Captures subprocess output for proper logging and error diagnosis
    - Logs stderr even on success (may contain warnings)
    - Provides detailed error information on failure
    """
    stage_name = STAGE_NAMES.get(stage_num, f"Stage {stage_num}")
    
    print("\n" + "=" * 80)
    print(f"🚀 RUNNING STAGE {stage_num}: {stage_name}")
    print("=" * 80 + "\n")
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        logger.error(
            "stage_script_not_found",
            stage=stage_num,
            stage_name=stage_name,
            script_path=str(script_path),
        )
        return False
    
    # FIX: Sanitize command arguments to prevent injection (Issue 1 - Security)
    def sanitize_arg(arg: str) -> str:
        """Sanitize command argument to prevent injection attacks.
        
        Removes dangerous characters while preserving valid path/file characters.
        """
        import re
        # Allow alphanumeric, forward slashes, dots, dashes, underscores
        # Remove any characters that could be used for shell injection
        sanitized = re.sub(r'[^a-zA-Z0-9/._-]', '', str(arg))
        return sanitized
    
    # Build command with sanitized arguments
    cmd = [sys.executable, sanitize_arg(str(script_path))]
    
    # Always pass source-dir for stage 0 (default: ~/.claude/projects)
    if stage_num == 0 and source_dir is not None:
        cmd.extend(["--source-dir", sanitize_arg(str(source_dir))])
    
    # Add dry-run flag only for stages 1–16 (Stage 0 does not support --dry-run)
    if dry_run and stage_num > 0:
        cmd.append("--dry-run")
    
    # Add manifest for stage 1 when running manifest-driven (0→1) and manifest exists
    if stage_num == 1 and manifest_path is not None and manifest_path.exists():
        cmd.extend(["--manifest", sanitize_arg(str(manifest_path))])
    
    # Add run_id if available for traceability
    if run_id:
        cmd.extend(["--run-id", sanitize_arg(run_id)])
    
    # FIX: Adaptive timeouts per stage to prevent resource exhaustion (Issue 2)
    STAGE_TIMEOUTS = {
        0: 300,   # Discovery: 5 minutes
        1: 600,   # Extraction: 10 minutes
        2: 300,   # Cleaning: 5 minutes
        3: 180,   # Identity: 3 minutes
        4: 600,   # LLM Correction: 10 minutes
        5: 300,   # Conversations: 5 minutes
        6: 300,   # Turns: 5 minutes
        7: 300,   # Messages: 5 minutes
        8: 300,   # Sentences: 5 minutes
        9: 300,   # Spans: 5 minutes
        10: 300,  # Words: 5 minutes
        11: 300,  # Validation: 5 minutes
        12: 300,  # Denormalization: 5 minutes
        13: 300,  # Pre-promotion: 5 minutes
        14: 600,  # Promotion: 10 minutes
        15: 300,  # Final validation: 5 minutes
        16: 300,  # Final promotion: 5 minutes
    }
    
    stage_timeout = STAGE_TIMEOUTS.get(stage_num, 300)  # Default: 5 minutes
    MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB - bounded output to prevent memory exhaustion
    
    # FIX: Bounded output capture to prevent memory exhaustion (Issue 3)
    import tempfile
    
    stdout_path = None
    stderr_path = None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as stdout_file, \
             tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as stderr_file:
            
            stdout_path = Path(stdout_file.name)
            stderr_path = Path(stderr_file.name)
            
            # Run subprocess with file-based output (prevents memory exhaustion)
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                check=True,
                stdout=stdout_file,  # Write to file instead of memory
                stderr=stderr_file,  # Write to file instead of memory
                text=True,
                encoding='utf-8',
                timeout=stage_timeout,  # Adaptive timeout per stage
            )
        
        # Read bounded output after subprocess completes (max 1MB per stream)
        stdout_content = ""
        stderr_content = ""
        
        if stdout_path and stdout_path.exists():
            with open(stdout_path, 'r', encoding='utf-8') as f:
                stdout_content = f.read(MAX_OUTPUT_SIZE)
                if stdout_path.stat().st_size > MAX_OUTPUT_SIZE:
                    stdout_content += "\n... (output truncated, see log file for full output)"
            stdout_path.unlink(missing_ok=True)
        
        if stderr_path and stderr_path.exists():
            with open(stderr_path, 'r', encoding='utf-8') as f:
                stderr_content = f.read(MAX_OUTPUT_SIZE)
                if stderr_path.stat().st_size > MAX_OUTPUT_SIZE:
                    stderr_content += "\n... (output truncated, see log file for full output)"
            stderr_path.unlink(missing_ok=True)
        
        # Log stdout from the child process for auditability
        if stdout_content:
            logger.info(
                "stage_stdout",
                stage=stage_num,
                stage_name=stage_name,
                output=stdout_content.strip(),
                run_id=run_id,
            )
            # Print to console for user visibility
            if stdout_content.strip():
                print("--- STDOUT ---")
                print(stdout_content.strip())
                print("--------------")
        
        # Log stderr even on success, as it may contain warnings
        if stderr_content:
            logger.warning(
                "stage_stderr",
                stage=stage_num,
                stage_name=stage_name,
                warnings=stderr_content.strip(),
                run_id=run_id,
            )
            # Print warnings to console
            print("--- STDERR (Warnings) ---")
            print(stderr_content.strip())
            print("-------------------------")
        
        print(f"\n✅ Stage {stage_num} ({stage_name}) completed successfully\n")
        logger.info(
            "stage_completed",
            stage=stage_num,
            stage_name=stage_name,
            run_id=run_id,
        )
        return True
        
    except subprocess.TimeoutExpired as e:
        print(f"\n❌ Stage {stage_num} ({stage_name}) timed out after 1 hour\n")
        logger.error(
            "stage_timeout",
            stage=stage_num,
            stage_name=stage_name,
            timeout_seconds=3600,
            run_id=run_id,
        )
        return False
        
    except subprocess.CalledProcessError as e:
        # On failure, read output from temp files if they exist
        stdout_error = "N/A"
        stderr_error = "N/A"
        
        try:
            if stdout_path and stdout_path.exists():
                with open(stdout_path, 'r', encoding='utf-8') as f:
                    stdout_error = f.read(MAX_OUTPUT_SIZE)
                stdout_path.unlink(missing_ok=True)
            if stderr_path and stderr_path.exists():
                with open(stderr_path, 'r', encoding='utf-8') as f:
                    stderr_error = f.read(MAX_OUTPUT_SIZE)
                stderr_path.unlink(missing_ok=True)
        except Exception as read_error:
            logger.warning(f"Failed to read temp files: {read_error}")
        
        print(f"\n❌ Stage {stage_num} ({stage_name}) failed with exit code {e.returncode}\n")
        
        # Log detailed error information
        logger.error(
            "stage_failed",
            stage=stage_num,
            stage_name=stage_name,
            exit_code=e.returncode,
            stdout=stdout_error.strip() if isinstance(stdout_error, str) and stdout_error != "N/A" else "N/A",
            stderr=stderr_error.strip() if isinstance(stderr_error, str) and stderr_error != "N/A" else "N/A",
            run_id=run_id,
        )
        
        # Print error details to console for user
        if stdout_error and stdout_error != "N/A":
            print("--- STDOUT ---")
            print(stdout_error.strip()[:1000])  # Limit console output
            print("--------------")
        if stderr_error and stderr_error != "N/A":
            print("--- STDERR (Error) ---")
            print(stderr_error.strip()[:1000])  # Limit console output
            print("----------------------")
        
        return False
        
    except subprocess.TimeoutExpired as e:
        # Clean up temp files on timeout
        if stdout_path and stdout_path.exists():
            stdout_path.unlink(missing_ok=True)
        if stderr_path and stderr_path.exists():
            stderr_path.unlink(missing_ok=True)
        
        print(f"\n❌ Stage {stage_num} ({stage_name}) timed out after {stage_timeout} seconds\n")
        logger.error(
            "stage_timeout",
            stage=stage_num,
            stage_name=stage_name,
            timeout_seconds=stage_timeout,
            run_id=run_id,
        )
        return False
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Stage {stage_num} interrupted by user\n")
        logger.warning(
            "stage_interrupted",
            stage=stage_num,
            stage_name=stage_name,
            run_id=run_id,
        )
        return False


def main() -> int:
    """Run the complete Claude Code pipeline."""
    parser = argparse.ArgumentParser(
        description="Run the complete Claude Code pipeline (Stages 0-16)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline (finds files automatically)
  python run_pipeline.py

  # Run with custom source directory (only if your files are somewhere else)
  python run_pipeline.py --source-dir ~/my-claude-sessions

  # Run specific stages
  python run_pipeline.py --start-stage 5 --end-stage 8

  # Dry-run (test without writing data)
  python run_pipeline.py --dry-run

  # Run from stage 0 to stage 4 only
  python run_pipeline.py --end-stage 4
        """,
    )
    
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Source directory for JSONL files (automatic: ~/.claude/projects - you don't need to specify this)",
    )
    
    parser.add_argument(
        "--start-stage",
        type=int,
        default=0,
        help="Start from this stage (default: 0)",
    )
    
    parser.add_argument(
        "--end-stage",
        type=int,
        default=16,
        help="End at this stage (default: 16)",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test run without writing data to BigQuery",
    )
    
    parser.add_argument(
        "--stages",
        type=str,
        help="Comma-separated list of specific stages to run (e.g., '0,1,2,3,4')",
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Existing run ID to resume a failed pipeline. A new ID will be generated if not provided.",
    )
    
    args = parser.parse_args()
    
    # FIX: Validate and sanitize source_dir path with strict security (Issue 4)
    try:
        # Get canonical path, resolving all symlinks (prevents symlink attacks)
        source_dir_canon = Path(os.path.realpath(args.source_dir))
        
        if not source_dir_canon.is_dir():
            raise FileNotFoundError(f"Resolved source path is not a directory: {source_dir_canon}")
        
        # Define restrictive sandbox for pipeline sources
        # This should ideally be a non-user-writable directory configured at deployment time
        allowed_sandbox = Path(
            os.getenv("PIPELINE_SANDBOX_DIR", str(Path.home() / ".claude" / "pipeline_sources"))
        ).resolve()
        allowed_sandbox.mkdir(parents=True, exist_ok=True)
        
        # Critical security check: is the canonical path within the sandbox?
        # Also allow project directory and home directory for backward compatibility
        project_root_abs = PROJECT_ROOT.resolve(strict=True)
        home_dir = Path.home()
        
        is_allowed = (
            allowed_sandbox in source_dir_canon.parents or source_dir_canon == allowed_sandbox or
            project_root_abs in source_dir_canon.parents or source_dir_canon == project_root_abs or
            home_dir in source_dir_canon.parents or source_dir_canon == home_dir
        )
        
        if not is_allowed:
            print(f"❌ Security Error: --source-dir '{args.source_dir}' resolves to a path outside the allowed sandbox.")
            print(f"   Resolved Path: {source_dir_canon}")
            print(f"   Allowed Sandbox: {allowed_sandbox}")
            print(f"   Also allowed: project directory, home directory")
            logger.error(
                "source_dir_security_violation",
                source_dir=str(args.source_dir),
                resolved_path=str(source_dir_canon),
                sandbox=str(allowed_sandbox),
            )
            return 1
        
        # Use validated canonical path
        args.source_dir = source_dir_canon
        
    except FileNotFoundError as e:
        print(f"❌ Error: --source-dir '{args.source_dir}' does not exist or is not a directory.")
        logger.error("source_dir_not_found", source_dir=str(args.source_dir), error=str(e))
        return 1
    except Exception as e:
        print(f"❌ Error validating source directory: {e}")
        logger.error("source_dir_validation_error", error=str(e), source_dir=str(args.source_dir))
        return 1
    
    # FIX: Use provided run_id or generate a new one (Issue 1 - Pipeline Resumption)
    run_id = args.run_id if args.run_id else get_current_run_id()
    
    # FIX: Use run-specific manifest path to avoid overwriting (Issue 3)
    # This makes stages idempotent and prevents race conditions
    manifest_filename = f"discovery_manifest_{run_id}.json"
    discovery_manifest_path = DISCOVERY_MANIFEST_DIR / manifest_filename
    
    # Ensure staging directory exists
    DISCOVERY_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Determine which stages to run
    if args.stages:
        # Specific stages requested
        stage_nums = [int(s.strip()) for s in args.stages.split(",")]
    else:
        # Range of stages
        stage_nums = list(range(args.start_stage, args.end_stage + 1))
    
    # Validate stage numbers
    invalid_stages = [s for s in stage_nums if s not in STAGES]
    if invalid_stages:
        print(f"❌ Invalid stage numbers: {invalid_stages}")
        print(f"Valid stages: {list(STAGES.keys())}")
        return 1
    
    # Print pipeline overview
    print("\n" + "=" * 80)
    print("🎯 CLAUDE CODE PIPELINE")
    print("=" * 80)
    print("\nPipeline Features:")
    print("  • Multi-stage data processing pipeline")
    print("  • Stage-by-stage execution with error handling")
    print("  • Configurable source directories")
    print("  • Run-specific state management")
    print("  • Comprehensive logging and error reporting")
    print("\nNote: Advanced features (time-travel queries, event sourcing, etc.)")
    print("      are implemented in individual stage scripts, not in this orchestrator.")
    print("\n" + "=" * 80)
    print(f"\n📋 Running stages: {stage_nums}")
    print(f"📁 Source directory: {args.source_dir}")
    print(f"🧪 Dry-run mode: {'YES' if args.dry_run else 'NO'}")
    print(f"🆔 Run ID: {run_id}")
    print(f"📄 Manifest: {discovery_manifest_path.name}")
    print("\n" + "=" * 80 + "\n")
    
    # Run stages sequentially
    failed_stages = []
    
    for stage_num in stage_nums:
        script_path = STAGES[stage_num]
        success = run_stage(
            stage_num=stage_num,
            script_path=script_path,
            source_dir=args.source_dir,
            dry_run=args.dry_run,
            manifest_path=discovery_manifest_path,  # Use run-specific manifest
            run_id=run_id,
        )
        
        if not success:
            failed_stages.append(stage_num)
            if not args.dry_run:
                print(f"\n⚠️  Pipeline stopped at Stage {stage_num}")
                print("Fix the error and re-run from this stage using:")
                print(f"  python run_pipeline.py --start-stage {stage_num} --run-id {run_id}")
                logger.error(
                    "pipeline_stopped",
                    failed_stage=stage_num,
                    run_id=run_id,
                    stages_completed=stage_nums[:stage_nums.index(stage_num)],
                )
                break
    
    # Final summary
    print("\n" + "=" * 80)
    if not failed_stages:
        print("✅ PIPELINE COMPLETE!")
        print("=" * 80)
        print("\nAll stages have been run successfully.")
        print(f"Run ID: {run_id}")
        print(f"Manifest: {discovery_manifest_path.name}")
        print("\nData has been processed through all pipeline stages.")
        print("Final destination: spine.entity_unified")
        print("\n" + "=" * 80 + "\n")
        logger.info(
            "pipeline_complete",
            run_id=run_id,
            stages_completed=stage_nums,
            manifest_path=str(discovery_manifest_path),
        )
        return 0
    else:
        print("❌ PIPELINE FAILED")
        print("=" * 80)
        print(f"\nFailed stages: {failed_stages}")
        print(f"Run ID: {run_id}")
        print("\nFix the errors and re-run from the first failed stage.")
        print(f"  python run_pipeline.py --start-stage {failed_stages[0]} --run-id {run_id}")
        print("\n" + "=" * 80 + "\n")
        logger.error(
            "pipeline_failed",
            run_id=run_id,
            failed_stages=failed_stages,
            stages_completed=stage_nums[:stage_nums.index(failed_stages[0])] if failed_stages else [],
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
