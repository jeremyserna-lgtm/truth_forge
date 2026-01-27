#!/usr/bin/env python3
"""
Pre-Flight Validation - Complete Fidelity Checks

Validates all pre-flight conditions before running the pipeline.
Ensures complete fidelity by checking:
- Source directory and JSONL files
- BigQuery project/dataset access
- spaCy installation and model
- Optional: Gemini CLI/API (for Stage 4)
- Identity service availability

Usage:
    python preflight_check.py [--source-dir PATH] [--strict]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Add scripts directory to path
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

try:
    from shared.constants import PROJECT_ID, DATASET_ID
    DEFAULT_SOURCE_DIR = Path.home() / ".claude" / "projects"
except ImportError:
    print("❌ Cannot import shared constants. Run from project root.")
    sys.exit(1)


def check_source_directory(source_dir: Path) -> Tuple[bool, List[str]]:
    """Check source directory exists and contains JSONL files.
    
    Args:
        source_dir: Path to source directory
    
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    
    if not source_dir.exists():
        issues.append(f"Source directory does not exist: {source_dir}")
        return False, issues
    
    if not source_dir.is_dir():
        issues.append(f"Source path is not a directory: {source_dir}")
        return False, issues
    
    # Check for JSONL files
    jsonl_files = list(source_dir.rglob("*.jsonl"))
    if not jsonl_files:
        issues.append(f"No JSONL files found in {source_dir}")
        return False, issues
    
    return True, []


def check_bigquery() -> Tuple[bool, List[str]]:
    """Check BigQuery project and dataset access.
    
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    
    try:
        from google.cloud import bigquery
    except ImportError:
        issues.append("google-cloud-bigquery not installed: pip install google-cloud-bigquery")
        return False, issues
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        # Check dataset exists
        try:
            dataset = client.get_dataset(DATASET_ID)
            # Dataset exists - good
        except Exception as e:
            issues.append(f"Dataset {DATASET_ID} not accessible: {e}")
            issues.append(f"  Create it: bq mk --dataset {PROJECT_ID}:{DATASET_ID}")
            return False, issues
        
        # Try a simple query to verify access
        try:
            test_query = f"SELECT 1 as test FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__` LIMIT 1"
            list(client.query(test_query).result())
        except Exception as e:
            issues.append(f"Cannot query dataset {DATASET_ID}: {e}")
            issues.append("  Check IAM permissions for BigQuery access")
            return False, issues
        
        return True, []
    
    except Exception as e:
        issues.append(f"BigQuery client error: {e}")
        issues.append("  Check GCP credentials: gcloud auth application-default login")
        return False, issues


def check_spacy() -> Tuple[bool, List[str]]:
    """Check spaCy installation and model.
    
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    
    try:
        import spacy
    except ImportError:
        issues.append("spaCy not installed: pip install spacy")
        return False, issues
    
    # Check for English model (default used in pipeline)
    # Common models: en_core_web_sm, en_core_web_md, en_core_web_lg
    model_name = "en_core_web_sm"  # Default model used in pipeline
    
    try:
        nlp = spacy.load(model_name)
        # Model loaded successfully
        return True, []
    except OSError:
        issues.append(f"spaCy model '{model_name}' not found")
        issues.append(f"  Download it: python -m spacy download {model_name}")
        return False, issues
    except Exception as e:
        issues.append(f"Error loading spaCy model: {e}")
        return False, issues


def check_gemini(strict: bool = False) -> Tuple[bool, List[str]]:
    """Check Gemini CLI or API availability (optional for Stage 4).
    
    Args:
        strict: If True, Gemini is required. If False, warnings only.
    
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    warnings = []
    
    # Check Gemini CLI (primary method)
    import shutil
    gemini_cli = shutil.which("gemini")
    if gemini_cli:
        return True, []  # CLI available - good to go
    
    warnings.append("Gemini CLI not found (primary method for Stage 4)")
    warnings.append("  Install: See Gemini CLI documentation")
    
    # Check Gemini API fallback (Secret Manager)
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        
        # Try to access the secret (don't read it, just check access)
        secret_name = f"projects/{PROJECT_ID}/secrets/Google_API_Key"
        try:
            client.get_secret(request={"name": secret_name})
            # Secret exists - API fallback available
            return True, warnings  # API available, but CLI preferred
        except Exception:
            warnings.append(f"Gemini API secret 'Google_API_Key' not found in Secret Manager")
            warnings.append(f"  Create it: gcloud secrets create Google_API_Key --data-file=-")
    except ImportError:
        warnings.append("google-cloud-secret-manager not installed (needed for API fallback)")
        warnings.append("  Install: pip install google-cloud-secret-manager")
    except Exception as e:
        warnings.append(f"Cannot access Secret Manager: {e}")
    
    if strict:
        issues.extend(warnings)
        return False, issues
    else:
        return True, warnings  # Optional - warnings only


def check_identity_service() -> Tuple[bool, List[str]]:
    """Check identity service availability.
    
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    
    try:
        from truth_forge.identity import generate_primitive_id
        # Service available
        return True, []
    except ImportError:
        try:
            from src.services.central_services.identity import generate_primitive_id
            return True, []
        except ImportError:
            issues.append("Identity service not available (Primitive.identity or src.services.central_services.identity)")
            return False, issues
    except Exception as e:
        issues.append(f"Identity service error: {e}")
        return False, issues


def main() -> int:
    """Run pre-flight validation checks."""
    parser = argparse.ArgumentParser(
        description="Pre-flight validation for Claude Code pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help=f"Source directory for JSONL files (default: {DEFAULT_SOURCE_DIR})",
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require Gemini (Stage 4 will fail without it)",
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 PRE-FLIGHT VALIDATION - CLAUDE CODE PIPELINE")
    print("=" * 80)
    print()
    
    all_valid = True
    all_issues: List[str] = []
    all_warnings: List[str] = []
    
    # 1. Source directory
    print("📁 Checking source directory...")
    valid, issues = check_source_directory(args.source_dir)
    if valid:
        jsonl_count = len(list(args.source_dir.rglob("*.jsonl")))
        print(f"   ✅ Source directory: {args.source_dir}")
        print(f"   ✅ Found {jsonl_count:,} JSONL files")
    else:
        print(f"   ❌ Source directory: {args.source_dir}")
        for issue in issues:
            print(f"      • {issue}")
        all_valid = False
        all_issues.extend(issues)
    print()
    
    # 2. BigQuery
    print("☁️  Checking BigQuery...")
    valid, issues = check_bigquery()
    if valid:
        print(f"   ✅ Project: {PROJECT_ID}")
        print(f"   ✅ Dataset: {DATASET_ID}")
    else:
        print(f"   ❌ BigQuery access failed")
        for issue in issues:
            print(f"      • {issue}")
        all_valid = False
        all_issues.extend(issues)
    print()
    
    # 3. spaCy
    print("🔤 Checking spaCy...")
    valid, issues = check_spacy()
    if valid:
        print("   ✅ spaCy installed and model available")
    else:
        print("   ❌ spaCy check failed")
        for issue in issues:
            print(f"      • {issue}")
        all_valid = False
        all_issues.extend(issues)
    print()
    
    # 4. Gemini (optional)
    print("🤖 Checking Gemini (optional for Stage 4)...")
    valid, messages = check_gemini(strict=args.strict)
    if valid and not messages:
        print("   ✅ Gemini CLI available")
    elif valid and messages:
        print("   ⚠️  Gemini: Warnings (optional)")
        for msg in messages:
            print(f"      • {msg}")
        all_warnings.extend(messages)
    else:
        print("   ❌ Gemini check failed (required with --strict)")
        for issue in messages:
            print(f"      • {issue}")
        all_valid = False
        all_issues.extend(messages)
    print()
    
    # 5. Identity service
    print("🆔 Checking identity service...")
    valid, issues = check_identity_service()
    if valid:
        print("   ✅ Identity service available")
    else:
        print("   ❌ Identity service check failed")
        for issue in issues:
            print(f"      • {issue}")
        all_valid = False
        all_issues.extend(issues)
    print()
    
    # Summary
    print("=" * 80)
    if all_valid:
        print("✅ ALL CHECKS PASSED - Pipeline ready to run!")
        print("=" * 80)
        if all_warnings:
            print()
            print("⚠️  Warnings (non-blocking):")
            for warning in all_warnings:
                print(f"   • {warning}")
        return 0
    else:
        print("❌ PRE-FLIGHT CHECKS FAILED")
        print("=" * 80)
        print()
        print("Issues to fix:")
        for issue in all_issues:
            print(f"   • {issue}")
        print()
        print("Fix the issues above and run preflight_check.py again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
