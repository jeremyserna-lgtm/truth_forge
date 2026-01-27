#!/usr/bin/env python3
"""Knowledge Atom Quality Assessment

Assesses knowledge atoms against the canonical schema to ensure quality and compliance.

Usage:
    python assess_knowledge_atoms.py [--stage N] [--all]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Add scripts directory to path
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from shared import get_pipeline_hold2_path, PIPELINE_NAME

try:
    from truth_forge.core import get_logger
except Exception:
    from src.services.central_services.core import get_logger

logger = get_logger(__name__)


# Canonical knowledge atom schema (from knowledge_atoms.json)
CANONICAL_SCHEMA = {
    "required_fields": [
        "atom_id",      # VARCHAR - Unique atom identifier (format: atom:xxxxxxxxxxxx)
        "type",         # VARCHAR - Atom type (observation, pattern, etc.)
        "content",      # TEXT - The atomic knowledge statement
        "source_name",  # VARCHAR - Source organism or agent
        "source_id",    # VARCHAR - Run/session/extraction ID for tracing
        "timestamp",    # TIMESTAMP - When the atom was created
        "metadata",     # JSON - Flexible JSON for extended fields
        "hash",         # VARCHAR - SHA256 content hash (first 16 chars)
    ],
    "atom_id_format": "atom:{hash12}",
    "hash_length": 16,  # First 16 chars of SHA256
}


def validate_atom_schema(atom: Dict[str, Any], stage: int) -> Dict[str, Any]:
    """Validate a knowledge atom against the canonical schema.
    
    Args:
        atom: Knowledge atom record
        stage: Stage number (for context)
    
    Returns:
        Dict with validation results: {"valid": bool, "errors": List, "warnings": List, "score": float}
    """
    errors = []
    warnings = []
    score = 100.0
    
    # Check required fields
    for field in CANONICAL_SCHEMA["required_fields"]:
        if field not in atom:
            errors.append(f"Missing required field: {field}")
            score -= 12.5  # Each required field is worth ~12.5 points
        else:
            # Validate field types and formats
            if field == "atom_id":
                if not atom[field].startswith("atom:"):
                    errors.append(f"atom_id must start with 'atom:' (got: {atom[field]})")
                    score -= 5.0
                elif len(atom[field].split(":")[1]) != 12:
                    warnings.append(f"atom_id hash should be 12 chars (got: {len(atom[field].split(':')[1])} chars)")
                    score -= 2.0
            
            elif field == "hash":
                if len(atom[field]) != CANONICAL_SCHEMA["hash_length"]:
                    errors.append(f"hash must be {CANONICAL_SCHEMA['hash_length']} chars (got: {len(atom[field])} chars)")
                    score -= 5.0
            
            elif field == "type":
                if not isinstance(atom[field], str):
                    errors.append(f"type must be a string (got: {type(atom[field])})")
                    score -= 5.0
                elif atom[field] not in ["observation", "pattern", "insight", "fact", "belief", "decision"]:
                    warnings.append(f"type '{atom[field]}' is not in common types (observation, pattern, insight, etc.)")
                    score -= 1.0
            
            elif field == "content":
                if not isinstance(atom[field], str):
                    errors.append(f"content must be a string (got: {type(atom[field])})")
                    score -= 5.0
                elif len(atom[field]) == 0:
                    errors.append("content cannot be empty")
                    score -= 10.0
            
            elif field == "metadata":
                if not isinstance(atom[field], dict):
                    errors.append(f"metadata must be a dict/JSON object (got: {type(atom[field])})")
                    score -= 5.0
    
    # Check for pipeline-specific fields (should be present but not required by canonical)
    pipeline_fields = ["pipeline", "stage", "run_id", "status"]
    for field in pipeline_fields:
        if field not in atom:
            warnings.append(f"Missing pipeline-specific field: {field} (helpful for router processing)")
            score -= 1.0
    
    # Validate hash matches content
    if "content" in atom and "hash" in atom:
        import hashlib
        expected_hash = hashlib.sha256(atom["content"].encode()).hexdigest()[:CANONICAL_SCHEMA["hash_length"]]
        if atom["hash"] != expected_hash:
            errors.append(f"hash does not match content (expected: {expected_hash}, got: {atom['hash']})")
            score -= 10.0
    
    # Validate atom_id format
    if "atom_id" in atom and "content" in atom and "source_name" in atom and "source_id" in atom:
        # atom_id should be deterministic based on source_name + source_id + content
        # We can't fully validate this without regenerating, but we can check format
        if not atom["atom_id"].startswith("atom:"):
            errors.append("atom_id must start with 'atom:'")
            score -= 5.0
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0.0, score),  # Don't go below 0
    }


def assess_stage_atoms(stage: int) -> Dict[str, Any]:
    """Assess knowledge atoms from a specific pipeline stage.
    
    Args:
        stage: Stage number (0-16)
    
    Returns:
        Dict with assessment results
    """
    hold2_path = get_pipeline_hold2_path(stage, PIPELINE_NAME)
    
    result = {
        "stage": stage,
        "hold2_path": str(hold2_path),
        "exists": False,
        "atoms_found": 0,
        "atoms_valid": 0,
        "atoms_invalid": 0,
        "total_score": 0.0,
        "average_score": 0.0,
        "atoms": [],
        "errors": [],
        "warnings": [],
    }
    
    if not hold2_path.exists():
        result["errors"].append(f"Pipeline HOLD₂ not found: {hold2_path}")
        return result
    
    result["exists"] = True
    
    try:
        with open(hold2_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    atom = json.loads(line)
                    result["atoms_found"] += 1
                    
                    # Validate atom
                    validation = validate_atom_schema(atom, stage)
                    result["total_score"] += validation["score"]
                    
                    atom_assessment = {
                        "line": line_num,
                        "atom_id": atom.get("atom_id", "MISSING"),
                        "type": atom.get("type", "MISSING"),
                        "validation": validation,
                    }
                    result["atoms"].append(atom_assessment)
                    
                    if validation["valid"]:
                        result["atoms_valid"] += 1
                    else:
                        result["atoms_invalid"] += 1
                        result["errors"].extend([f"Line {line_num}: {e}" for e in validation["errors"]])
                    
                    if validation["warnings"]:
                        result["warnings"].extend([f"Line {line_num}: {w}" for w in validation["warnings"]])
                
                except json.JSONDecodeError as e:
                    result["errors"].append(f"Invalid JSON at line {line_num}: {e}")
                    result["atoms_invalid"] += 1
                except Exception as e:
                    result["errors"].append(f"Error processing line {line_num}: {e}")
                    result["atoms_invalid"] += 1
        
        if result["atoms_found"] > 0:
            result["average_score"] = result["total_score"] / result["atoms_found"]
    
    except Exception as e:
        result["errors"].append(f"Failed to read pipeline HOLD₂: {e}")
        logger.error(
            f"Failed to assess knowledge atoms for stage {stage}: {e}",
            extra={"stage": stage, "hold2_path": str(hold2_path), "error": str(e)},
            exc_info=True,
        )
    
    return result


def assess_all_stages() -> Dict[str, Any]:
    """Assess knowledge atoms from all pipeline stages.
    
    Returns:
        Dict with assessment results for all stages
    """
    results = {
        "stages": {},
        "summary": {
            "total_stages": 17,
            "stages_with_atoms": 0,
            "total_atoms": 0,
            "total_valid": 0,
            "total_invalid": 0,
            "overall_average_score": 0.0,
        },
    }
    
    total_score = 0.0
    total_atoms = 0
    
    for stage in range(17):
        stage_result = assess_stage_atoms(stage)
        results["stages"][stage] = stage_result
        
        if stage_result["atoms_found"] > 0:
            results["summary"]["stages_with_atoms"] += 1
            results["summary"]["total_atoms"] += stage_result["atoms_found"]
            results["summary"]["total_valid"] += stage_result["atoms_valid"]
            results["summary"]["total_invalid"] += stage_result["atoms_invalid"]
            total_score += stage_result["total_score"]
            total_atoms += stage_result["atoms_found"]
    
    if total_atoms > 0:
        results["summary"]["overall_average_score"] = total_score / total_atoms
    
    return results


def print_assessment_report(results: Dict[str, Any]) -> None:
    """Print a formatted assessment report.
    
    Args:
        results: Assessment results dict
    """
    print("\n" + "="*80)
    print("KNOWLEDGE ATOM QUALITY ASSESSMENT")
    print("="*80)
    
    if "stages" in results:
        # All stages assessment
        print(f"\nSummary:")
        print(f"  Stages with atoms: {results['summary']['stages_with_atoms']}/{results['summary']['total_stages']}")
        print(f"  Total atoms: {results['summary']['total_atoms']}")
        print(f"  Valid atoms: {results['summary']['total_valid']}")
        print(f"  Invalid atoms: {results['summary']['total_invalid']}")
        print(f"  Overall average score: {results['summary']['overall_average_score']:.1f}/100")
        
        print(f"\nStage Details:")
        for stage_num in sorted(results["stages"].keys()):
            stage_result = results["stages"][stage_num]
            if stage_result["atoms_found"] > 0:
                status_icon = "✅" if stage_result["atoms_valid"] == stage_result["atoms_found"] else "⚠️"
                print(f"\n  {status_icon} Stage {stage_num}:")
                print(f"      Atoms: {stage_result['atoms_found']} found, {stage_result['atoms_valid']} valid, {stage_result['atoms_invalid']} invalid")
                print(f"      Average score: {stage_result['average_score']:.1f}/100")
                print(f"      Path: {stage_result['hold2_path']}")
                
                if stage_result["errors"]:
                    print(f"      Errors ({len(stage_result['errors'])}):")
                    for error in stage_result["errors"][:5]:  # Show first 5
                        print(f"        - {error}")
                    if len(stage_result["errors"]) > 5:
                        print(f"        ... and {len(stage_result['errors']) - 5} more")
                
                if stage_result["warnings"]:
                    print(f"      Warnings ({len(stage_result['warnings'])}):")
                    for warning in stage_result["warnings"][:3]:  # Show first 3
                        print(f"        - {warning}")
                    if len(stage_result["warnings"]) > 3:
                        print(f"        ... and {len(stage_result['warnings']) - 3} more")
                
                # Show atom details
                for atom_assessment in stage_result["atoms"][:2]:  # Show first 2
                    print(f"      Atom {atom_assessment['line']}:")
                    print(f"        atom_id: {atom_assessment['atom_id']}")
                    print(f"        type: {atom_assessment['type']}")
                    print(f"        Score: {atom_assessment['validation']['score']:.1f}/100")
                    if atom_assessment["validation"]["errors"]:
                        print(f"        Errors: {', '.join(atom_assessment['validation']['errors'][:2])}")
            elif stage_result["exists"]:
                print(f"\n  ⚠️  Stage {stage_num}: HOLD₂ exists but no atoms found")
            else:
                print(f"\n  ○ Stage {stage_num}: No HOLD₂ file (stage not run yet)")
    
    else:
        # Single stage assessment
        print(f"\nStage {results['stage']} Assessment:")
        print(f"  Path: {results['hold2_path']}")
        print(f"  Exists: {results['exists']}")
        print(f"  Atoms found: {results['atoms_found']}")
        print(f"  Valid: {results['atoms_valid']}")
        print(f"  Invalid: {results['atoms_invalid']}")
        print(f"  Average score: {results['average_score']:.1f}/100")
        
        if results["errors"]:
            print(f"\n  Errors ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"    - {error}")
        
        if results["warnings"]:
            print(f"\n  Warnings ({len(results['warnings'])}):")
            for warning in results["warnings"]:
                print(f"    - {warning}")
        
        if results["atoms"]:
            print(f"\n  Atom Details:")
            for atom_assessment in results["atoms"]:
                print(f"    Line {atom_assessment['line']}:")
                print(f"      atom_id: {atom_assessment['atom_id']}")
                print(f"      type: {atom_assessment['type']}")
                print(f"      Score: {atom_assessment['validation']['score']:.1f}/100")
                if atom_assessment["validation"]["errors"]:
                    print(f"      Errors: {', '.join(atom_assessment['validation']['errors'])}")
                if atom_assessment["validation"]["warnings"]:
                    print(f"      Warnings: {', '.join(atom_assessment['validation']['warnings'])}")
    
    print("\n" + "="*80)


def main() -> int:
    """Main entry point for assessment."""
    parser = argparse.ArgumentParser(
        description="Assess knowledge atom quality against canonical schema"
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=range(17),
        help="Assess atoms from specific stage only (0-16)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Assess atoms from all stages (default)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.stage is not None:
            # Assess specific stage
            result = assess_stage_atoms(args.stage)
            print_assessment_report(result)
            return 0 if result["atoms_invalid"] == 0 else 1
        else:
            # Assess all stages
            results = assess_all_stages()
            print_assessment_report(results)
            
            # Return non-zero if any atoms are invalid
            if results["summary"]["total_invalid"] > 0:
                return 1
            return 0
    
    except Exception as e:
        logger.error(
            f"Assessment failed: {e}",
            exc_info=True,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
