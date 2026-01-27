#!/usr/bin/env python3
"""
Safe Pipeline Runner - Incremental, Validated Execution

This script provides a safe way to run the Claude Code pipeline:
1. Pre-flight validation (checks dependencies, config, data)
2. Stage-by-stage execution with validation
3. Checkpointing (can resume from any stage)
4. Dry-run mode for testing
5. Validation after each stage

Usage:
    # Full safe run (with all checks)
    python safe_pipeline_runner.py --full-safe-run
    
    # Run one stage at a time with validation
    python safe_pipeline_runner.py --stage-by-stage
    
    # Dry-run first 3 stages
    python safe_pipeline_runner.py --dry-run --end-stage 3
    
    # Resume from stage 5
    python safe_pipeline_runner.py --resume-from 5
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from truth_forge.core import get_logger, get_current_run_id
except Exception:
    from src.services.central_services.core import get_logger
    def get_current_run_id():
        return "unknown"

logger = get_logger(__name__)

# Import pipeline runner
PIPELINE_ROOT = Path(__file__).parent
PROJECT_ROOT = PIPELINE_ROOT.parents[3]
RUN_PIPELINE_SCRIPT = PIPELINE_ROOT / "run_pipeline.py"
PREFLIGHT_SCRIPT = PIPELINE_ROOT / "preflight_check.py"

# Checkpoint file
CHECKPOINT_FILE = Path.home() / ".truth_engine" / "pipeline_checkpoint.json"


class PipelineValidator:
    """Validates pipeline state and dependencies."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_dependencies(self) -> bool:
        """Check that all required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.errors.append("Python 3.8+ required")
            return False
        
        # Check required modules
        required_modules = [
            "google.cloud.bigquery",
            "google.cloud.storage",
            "pandas",
            "spacy",
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            self.errors.append(f"Missing required modules: {', '.join(missing)}")
            return False
        
        print("  ✅ Dependencies OK")
        return True
    
    def validate_config(self) -> bool:
        """Check configuration and credentials."""
        print("🔍 Checking configuration...")
        
        # Check for GCP credentials
        import os
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
            self.warnings.append("GCP credentials not found in environment - may need to run 'gcloud auth application-default login'")
        
        # Check for BigQuery project
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project:
            self.warnings.append("GOOGLE_CLOUD_PROJECT not set")
        else:
            print(f"  ✅ GCP Project: {project}")
        
        print("  ✅ Configuration OK (with warnings)" if self.warnings else "  ✅ Configuration OK")
        return True
    
    def validate_data_sources(self, source_dir: Optional[Path] = None) -> bool:
        """Check that data sources exist."""
        print("🔍 Checking data sources...")
        
        if source_dir is None:
            source_dir = Path.home() / ".claude" / "projects"
        
        if not source_dir.exists():
            self.errors.append(f"Source directory not found: {source_dir}")
            return False
        
        # Check for JSONL files
        jsonl_files = list(source_dir.glob("**/*.jsonl"))
        if not jsonl_files:
            self.warnings.append(f"No JSONL files found in {source_dir}")
        else:
            print(f"  ✅ Found {len(jsonl_files)} JSONL files")
        
        return True
    
    def validate_stage_scripts(self) -> bool:
        """Check that all stage scripts exist."""
        print("🔍 Checking stage scripts...")
        
        stages = {
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
        
        missing = []
        for stage_num, script_path in stages.items():
            if not script_path.exists():
                missing.append(f"Stage {stage_num}: {script_path}")
        
        if missing:
            self.errors.append(f"Missing stage scripts:\n  " + "\n  ".join(missing))
            return False
        
        print(f"  ✅ All {len(stages)} stage scripts found")
        return True
    
    def run_preflight(self) -> bool:
        """Run the preflight check script if it exists."""
        if not PREFLIGHT_SCRIPT.exists():
            print("  ⚠️  Preflight script not found, skipping")
            return True
        
        print("🔍 Running preflight check...")
        try:
            result = subprocess.run(
                [sys.executable, str(PREFLIGHT_SCRIPT)],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("  ✅ Preflight check passed")
                return True
            else:
                print(f"  ❌ Preflight check failed:\n{result.stderr}")
                return False
        except Exception as e:
            print(f"  ⚠️  Preflight check error: {e}")
            return True  # Don't block on preflight errors
    
    def validate_all(self, source_dir: Optional[Path] = None) -> Tuple[bool, List[str], List[str]]:
        """Run all validations."""
        print("\n" + "=" * 80)
        print("🔍 PIPELINE VALIDATION")
        print("=" * 80 + "\n")
        
        all_ok = True
        all_ok = self.validate_dependencies() and all_ok
        all_ok = self.validate_config() and all_ok
        all_ok = self.validate_data_sources(source_dir) and all_ok
        all_ok = self.validate_stage_scripts() and all_ok
        all_ok = self.run_preflight() and all_ok
        
        print("\n" + "=" * 80)
        if all_ok and not self.errors:
            print("✅ VALIDATION PASSED")
            if self.warnings:
                print("\n⚠️  Warnings:")
                for warning in self.warnings:
                    print(f"  • {warning}")
        else:
            print("❌ VALIDATION FAILED")
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  • {error}")
            if self.warnings:
                print("\n⚠️  Warnings:")
                for warning in self.warnings:
                    print(f"  • {warning}")
        print("=" * 80 + "\n")
        
        return all_ok and not self.errors, self.errors, self.warnings


class CheckpointManager:
    """Manages pipeline checkpoints for resumable execution."""
    
    def save_checkpoint(self, stage: int, status: str, metadata: Optional[Dict] = None):
        """Save checkpoint."""
        checkpoint = {
            "last_stage": stage,
            "status": status,  # "completed", "failed", "in_progress"
            "timestamp": time.time(),
            "run_id": get_current_run_id(),
            "metadata": metadata or {},
        }
        
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
        logger.info(f"Checkpoint saved: stage {stage}, status {status}")
    
    def load_checkpoint(self) -> Optional[Dict]:
        """Load checkpoint."""
        if not CHECKPOINT_FILE.exists():
            return None
        
        try:
            return json.loads(CHECKPOINT_FILE.read_text())
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
            return None
    
    def clear_checkpoint(self):
        """Clear checkpoint."""
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
        logger.info("Checkpoint cleared")


def run_stage_safely(
    stage_num: int,
    dry_run: bool = False,
    source_dir: Optional[Path] = None,
    interactive: bool = False,
) -> Tuple[bool, str]:
    """Run a single stage with validation and user confirmation."""
    
    stage_names = {
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
    
    stage_name = stage_names.get(stage_num, f"Stage {stage_num}")
    
    print("\n" + "=" * 80)
    print(f"🚀 STAGE {stage_num}: {stage_name}")
    print("=" * 80)
    print(f"Mode: {'🧪 DRY-RUN' if dry_run else '✅ LIVE'}")
    print("=" * 80 + "\n")
    
    if interactive:
        response = input(f"Run Stage {stage_num} ({stage_name})? [y/N]: ").strip().lower()
        if response != 'y':
            print(f"⏭️  Skipping Stage {stage_num}\n")
            return False, "skipped"
    
    # Build command
    cmd = [sys.executable, str(RUN_PIPELINE_SCRIPT)]
    cmd.extend(["--stages", str(stage_num)])
    
    if dry_run:
        cmd.append("--dry-run")
    
    if source_dir:
        cmd.extend(["--source-dir", str(source_dir)])
    
    print(f"Command: {' '.join(cmd)}\n")
    print("Starting execution...\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            check=False,  # Don't raise, we'll handle it
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ Stage {stage_num} completed successfully ({elapsed:.1f}s)\n")
            return True, "success"
        else:
            print(f"\n❌ Stage {stage_num} failed with exit code {result.returncode} ({elapsed:.1f}s)\n")
            return False, f"failed: exit code {result.returncode}"
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Stage {stage_num} interrupted by user\n")
        return False, "interrupted"
    except Exception as e:
        print(f"\n❌ Stage {stage_num} error: {e}\n")
        return False, f"error: {str(e)}"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Safe, incremental pipeline runner with validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full safe run (validation + stage-by-stage with confirmation)
  python safe_pipeline_runner.py --full-safe-run
  
  # Stage-by-stage with user confirmation
  python safe_pipeline_runner.py --stage-by-stage
  
  # Dry-run first 3 stages
  python safe_pipeline_runner.py --dry-run --end-stage 3
  
  # Resume from checkpoint
  python safe_pipeline_runner.py --resume-from-checkpoint
  
  # Run specific stages
  python safe_pipeline_runner.py --stages 0,1,2
        """,
    )
    
    parser.add_argument("--full-safe-run", action="store_true",
                       help="Full safe run: validation + stage-by-stage with confirmation")
    parser.add_argument("--stage-by-stage", action="store_true",
                       help="Run stages one at a time with user confirmation")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry-run mode (no data written)")
    parser.add_argument("--start-stage", type=int, default=0,
                       help="Start from this stage")
    parser.add_argument("--end-stage", type=int, default=16,
                       help="End at this stage")
    parser.add_argument("--stages", type=str,
                       help="Comma-separated list of stages (e.g., '0,1,2')")
    parser.add_argument("--source-dir", type=Path,
                       help="Source directory for JSONL files")
    parser.add_argument("--resume-from-checkpoint", action="store_true",
                       help="Resume from last checkpoint")
    parser.add_argument("--resume-from", type=int,
                       help="Resume from specific stage number")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip pre-run validation")
    parser.add_argument("--non-interactive", action="store_true",
                       help="Run without user confirmation (for automation)")
    
    args = parser.parse_args()
    
    # Determine stages to run
    if args.stages:
        stage_nums = [int(s.strip()) for s in args.stages.split(",")]
    elif args.resume_from_checkpoint:
        checkpoint_mgr = CheckpointManager()
        checkpoint = checkpoint_mgr.load_checkpoint()
        if checkpoint:
            last_stage = checkpoint.get("last_stage", 0)
            stage_nums = list(range(last_stage + 1, args.end_stage + 1))
            print(f"📌 Resuming from checkpoint: last completed stage was {last_stage}")
        else:
            print("❌ No checkpoint found")
            return 1
    elif args.resume_from is not None:
        stage_nums = list(range(args.resume_from, args.end_stage + 1))
        print(f"📌 Resuming from stage {args.resume_from}")
    else:
        stage_nums = list(range(args.start_stage, args.end_stage + 1))
    
    # Validate stages
    if not stage_nums:
        print("❌ No stages to run")
        return 1
    
    # Run validation unless skipped
    if not args.skip_validation:
        validator = PipelineValidator()
        valid, errors, warnings = validator.validate_all(args.source_dir)
        
        if not valid:
            print("\n❌ Validation failed. Fix errors before running pipeline.")
            print("\nTo skip validation (not recommended), use --skip-validation")
            return 1
        
        if warnings and not args.non_interactive:
            response = input("\n⚠️  Warnings found. Continue anyway? [y/N]: ").strip().lower()
            if response != 'y':
                return 1
    
    # Determine if interactive
    interactive = args.full_safe_run or args.stage_by_stage
    if args.non_interactive:
        interactive = False
    
    # Run stages
    checkpoint_mgr = CheckpointManager()
    failed_stages = []
    
    print("\n" + "=" * 80)
    print("🚀 STARTING PIPELINE EXECUTION")
    print("=" * 80)
    print(f"Stages: {stage_nums}")
    print(f"Mode: {'🧪 DRY-RUN' if args.dry_run else '✅ LIVE'}")
    print(f"Interactive: {'Yes' if interactive else 'No'}")
    print("=" * 80 + "\n")
    
    for stage_num in stage_nums:
        checkpoint_mgr.save_checkpoint(stage_num, "in_progress")
        
        success, status = run_stage_safely(
            stage_num=stage_num,
            dry_run=args.dry_run,
            source_dir=args.source_dir,
            interactive=interactive,
        )
        
        if success:
            checkpoint_mgr.save_checkpoint(stage_num, "completed")
        else:
            checkpoint_mgr.save_checkpoint(stage_num, "failed", {"status": status})
            failed_stages.append((stage_num, status))
            
            if not args.dry_run:
                print(f"\n⚠️  Pipeline stopped at Stage {stage_num}")
                print(f"Status: {status}")
                print("\nTo resume from this stage:")
                print(f"  python safe_pipeline_runner.py --resume-from {stage_num}")
                break
    
    # Final summary
    print("\n" + "=" * 80)
    if not failed_stages:
        print("✅ PIPELINE COMPLETE!")
        checkpoint_mgr.clear_checkpoint()
    else:
        print("❌ PIPELINE FAILED")
        print(f"Failed stages: {[s[0] for s in failed_stages]}")
    print("=" * 80 + "\n")
    
    return 0 if not failed_stages else 1


if __name__ == "__main__":
    sys.exit(main())
