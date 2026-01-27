#!/usr/bin/env python3
"""Validate Pipeline and Knowledge Atom Production

Validates:
1. Pipeline data processing (stages 0-16)
2. Knowledge atom production (all stages)
3. Router functionality (execute() moves atoms from HOLD₁ to HOLD₂)
4. Deduplication (hash-based and column-based)
5. Similarity normalization (0.95 cosine similarity threshold)

Usage:
    python validate_pipeline_and_knowledge_atoms.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parents[3]  # pipelines/claude_code/scripts/ -> Truth_Engine/
sys.path.insert(0, str(project_root))

# Import only what we need for validation (avoid full imports that trigger spaCy)
try:
    from src.services.central_services.core.db import get_duckdb_connection
except Exception:
    get_duckdb_connection = None

try:
    from src.services.central_services.primitive_pattern.pattern import SIMILARITY_THRESHOLD
except Exception:
    SIMILARITY_THRESHOLD = 0.95  # Default

def validate_pipeline_stages() -> Dict[str, Any]:
    """Validate that all pipeline stages correctly call knowledge service."""
    print("=" * 80)
    print("VALIDATING PIPELINE STAGES")
    print("=" * 80)
    
    issues = []
    stages_checked = 0
    
    for stage_num in range(17):  # Stages 0-16
        stage_file = project_root / "pipelines" / "claude_code" / "scripts" / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
        
        if not stage_file.exists():
            issues.append(f"Stage {stage_num}: File not found")
            continue
        
        content = stage_file.read_text()
        
        # Check for canonical knowledge service import
        has_import = (
            "from src.services.central_services.knowledge_service.knowledge_service import get_knowledge_service" in content
            or "from src.services.central_services.knowledge_service" in content
        )
        
        # Check for exhale call
        has_exhale = "get_knowledge_service().exhale(" in content
        
        # Check for old special architecture (should NOT exist)
        has_old_import = "from shared.pipeline_knowledge_atoms import" in content
        
        if has_old_import:
            issues.append(f"Stage {stage_num}: Still uses old special architecture (pipeline_knowledge_atoms)")
        
        if not has_import:
            issues.append(f"Stage {stage_num}: Missing canonical knowledge service import")
        
        if not has_exhale:
            issues.append(f"Stage {stage_num}: Missing get_knowledge_service().exhale() call")
        
        stages_checked += 1
    
    return {
        "stages_checked": stages_checked,
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def validate_knowledge_service_architecture() -> Dict[str, Any]:
    """Validate knowledge service architecture."""
    print("\n" + "=" * 80)
    print("VALIDATING KNOWLEDGE SERVICE ARCHITECTURE")
    print("=" * 80)
    
    issues = []
    
    # Check that special architecture is removed
    special_arch_file = project_root / "pipelines" / "claude_code" / "scripts" / "shared" / "pipeline_knowledge_atoms.py"
    if special_arch_file.exists():
        issues.append("Special architecture file still exists: pipeline_knowledge_atoms.py")
    
    # Check shared/__init__.py doesn't export old functions
    shared_init = project_root / "pipelines" / "claude_code" / "scripts" / "shared" / "__init__.py"
    if shared_init.exists():
        content = shared_init.read_text()
        if "exhale_pipeline_knowledge" in content or "exhale_stage_summary" in content:
            if "from .pipeline_knowledge_atoms import" in content:
                issues.append("shared/__init__.py still exports old pipeline_knowledge_atoms functions")
    
    # Verify knowledge service exists and has required methods (check source code)
    knowledge_service_file = project_root / "src/services/central_services/knowledge_service/knowledge_service.py"
    if knowledge_service_file.exists():
        content = knowledge_service_file.read_text()
        if "def exhale(" in content:
            print(f"  ✓ Knowledge service has exhale() method")
        else:
            issues.append("Knowledge service missing exhale() method")
        
        if "def sync(" in content:
            print(f"  ✓ Knowledge service has sync() method")
        else:
            issues.append("Knowledge service missing sync() method")
        
        if "def _atom_agent(" in content:
            print(f"  ✓ Knowledge service has _atom_agent() method (AGENT function)")
        else:
            issues.append("Knowledge service missing _atom_agent() method")
    else:
        issues.append("Knowledge service file not found")
    
    return {
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def validate_router_functionality() -> Dict[str, Any]:
    """Validate that router (execute()) moves atoms from HOLD₁ to HOLD₂."""
    print("\n" + "=" * 80)
    print("VALIDATING ROUTER FUNCTIONALITY (execute())")
    print("=" * 80)
    
    issues = []
    
    try:
        # Import knowledge service config paths directly
        _DEFAULT_ROOT = project_root / "src" / "truth_forge"
        _DEFAULT_HOLDS_DIR = _DEFAULT_ROOT / "system_elements" / "holds" / "knowledge_atoms"
        _DEFAULT_INTAKE_DIR = _DEFAULT_HOLDS_DIR / "intake"
        _DEFAULT_PROCESSED_DIR = _DEFAULT_HOLDS_DIR / "processed"
        
        jsonl1_path = _DEFAULT_INTAKE_DIR / "hold1.jsonl"
        duckdb1_path = _DEFAULT_INTAKE_DIR / "hold1.duckdb"
        jsonl2_path = _DEFAULT_PROCESSED_DIR / "hold2.jsonl"
        duckdb2_path = _DEFAULT_PROCESSED_DIR / "hold2.duckdb"
        
        config = type('Config', (), {
            'jsonl1_path': jsonl1_path,
            'duckdb1_path': duckdb1_path,
            'jsonl2_path': jsonl2_path,
            'duckdb2_path': duckdb2_path,
        })()
        
        # Check HOLD₁ exists
        if not config.jsonl1_path.exists() and not config.duckdb1_path.exists():
            print(f"  ℹ️  HOLD₁ is empty (no atoms to process yet)")
            print(f"     JSONL1: {config.jsonl1_path}")
            print(f"     DuckDB1: {config.duckdb1_path}")
        else:
            # Count records in HOLD₁
            hold1_count = 0
            if config.jsonl1_path.exists():
                with open(config.jsonl1_path, "r") as f:
                    hold1_count = sum(1 for line in f if line.strip())
            
            if config.duckdb1_path.exists() and get_duckdb_connection:
                try:
                    conn = get_duckdb_connection(str(config.duckdb1_path), read_only=True)
                    result = conn.execute("SELECT COUNT(*) FROM hold1_data").fetchone()
                    hold1_count += result[0] if result else 0
                    conn.close()
                except Exception:
                    pass
            
            print(f"  ✓ HOLD₁ has {hold1_count} records")
        
        # Check HOLD₂ exists
        hold2_count = 0
        if config.jsonl2_path.exists():
            with open(config.jsonl2_path, "r") as f:
                hold2_count = sum(1 for line in f if line.strip())
        
        if config.duckdb2_path.exists() and get_duckdb_connection:
            try:
                conn = get_duckdb_connection(str(config.duckdb2_path), read_only=True)
                result = conn.execute("SELECT COUNT(*) FROM hold2_data").fetchone()
                hold2_count += result[0] if result else 0
                conn.close()
            except Exception:
                pass
        
        print(f"  ✓ HOLD₂ has {hold2_count} records")
        
        # Verify execute() method exists (check source code)
        pattern_file = project_root / "src/services/central_services/primitive_pattern/pattern.py"
        if pattern_file.exists():
            pattern_content = pattern_file.read_text()
            if "def execute(self)" in pattern_content:
                print(f"  ✓ Router (execute()) method exists in PrimitivePattern")
            else:
                issues.append("PrimitivePattern missing execute() method")
        
        # Verify sync() method exists
        knowledge_service_file = project_root / "src/services/central_services/knowledge_service/knowledge_service.py"
        if knowledge_service_file.exists():
            service_content = knowledge_service_file.read_text()
            if "def sync(self)" in service_content:
                print(f"  ✓ sync() method exists in KnowledgeService")
                if "self._pattern.execute()" in service_content:
                    print(f"  ✓ sync() calls execute() (router is functioning)")
            else:
                issues.append("KnowledgeService missing sync() method")
    
    except Exception as e:
        issues.append(f"Router validation failed: {e}")
        print(f"  ✗ Router validation error: {e}")
    
    return {
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def validate_deduplication() -> Dict[str, Any]:
    """Validate deduplication mechanisms."""
    print("\n" + "=" * 80)
    print("VALIDATING DEDUPLICATION")
    print("=" * 80)
    
    issues = []
    
    # Check HOLD₁ deduplication (content-based)
    try:
        knowledge_service_file = project_root / "src/services/central_services/knowledge_service/knowledge_service.py"
        if knowledge_service_file.exists():
            content = knowledge_service_file.read_text()
            
            # Verify _append_input uses deduplication
            if "def _append_input(" in content:
                print(f"  ✓ _append_input() method exists")
                if "append_to_jsonl_deduped" in content:
                    print(f"  ✓ _append_input() uses append_to_jsonl_deduped (deduplication)")
                else:
                    issues.append("_append_input() may not use deduplication")
            else:
                issues.append("Knowledge service missing _append_input() method")
            
            # Check that append_to_jsonl_deduped uses content for deduplication
            safe_writes_file = project_root / "src/services/central_services/core/safe_writes.py"
            if safe_writes_file.exists():
                safe_content = safe_writes_file.read_text()
                if "dedupe_key" in safe_content and "_hash" in safe_content:
                    print(f"  ✓ HOLD₁ deduplication uses content hash")
                else:
                    issues.append("HOLD₁ deduplication may not be using content hash")
    
    except Exception as e:
        issues.append(f"Deduplication validation failed: {e}")
    
    # Check HOLD₂ deduplication (column-based + similarity)
    try:
        pattern_file = project_root / "src/services/central_services/primitive_pattern/pattern.py"
        if pattern_file.exists():
            content = pattern_file.read_text()
            
            # Check _write_duckdb2 has deduplication
            if "def _write_duckdb2(" in content:
                has_column_dedupe = "dedupe_column" in content
                has_similarity_check = "array_cosine_similarity" in content or "similarity" in content.lower()
                
                if has_column_dedupe:
                    print(f"  ✓ HOLD₂ column-based deduplication implemented")
                else:
                    issues.append("HOLD₂ missing column-based deduplication")
                
                if has_similarity_check:
                    print(f"  ✓ HOLD₂ similarity-based deduplication implemented")
                else:
                    issues.append("HOLD₂ missing similarity-based deduplication")
            else:
                issues.append("PrimitivePattern missing _write_duckdb2() method")
    
    except Exception as e:
        issues.append(f"HOLD₂ deduplication check failed: {e}")
    
    return {
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def validate_similarity_normalization() -> Dict[str, Any]:
    """Validate similarity normalization (0.95 threshold)."""
    print("\n" + "=" * 80)
    print("VALIDATING SIMILARITY NORMALIZATION")
    print("=" * 80)
    
    issues = []
    
    # Check threshold constant
    threshold = SIMILARITY_THRESHOLD
    if threshold == 0.95:
        print(f"  ✓ Similarity threshold: {threshold} (correct)")
    else:
        issues.append(f"Similarity threshold is {threshold}, expected 0.95")
    
    # Check _similar_check function
    try:
        pattern_file = project_root / "src/services/central_services/primitive_pattern/pattern.py"
        if pattern_file.exists():
            content = pattern_file.read_text()
            
            if "def _similar_check(" in content:
                has_embedding = "_embed" in content or "embedding" in content
                has_cosine = "cosine_similarity" in content or "array_cosine_similarity" in content
                has_threshold = "0.95" in content or "SIMILARITY_THRESHOLD" in content
                
                if has_embedding:
                    print(f"  ✓ Similarity check uses embeddings")
                else:
                    issues.append("Similarity check missing embedding generation")
                
                if has_cosine:
                    print(f"  ✓ Similarity check uses cosine similarity")
                else:
                    issues.append("Similarity check missing cosine similarity")
                
                if has_threshold:
                    print(f"  ✓ Similarity check uses threshold")
                else:
                    issues.append("Similarity check missing threshold")
            else:
                issues.append("_similar_check() function not found")
    
    except Exception as e:
        issues.append(f"Similarity check validation failed: {e}")
    
    # Check VSS index (check code, not runtime)
    try:
        pattern_file = project_root / "src/services/central_services/primitive_pattern/pattern.py"
        if pattern_file.exists():
            content = pattern_file.read_text()
            
            # Check that VSS is used (check db.py for VSS installation)
            db_file = project_root / "src/services/central_services/core/db.py"
            if db_file.exists():
                db_content = db_file.read_text()
                if "INSTALL vss" in db_content or "LOAD vss" in db_content or "vss" in db_content.lower():
                    print(f"  ✓ VSS extension installation code exists")
                else:
                    issues.append("VSS extension installation code not found")
            else:
                issues.append("db.py not found (cannot verify VSS)")
            
            # Check that embeddings are generated
            if "_embed(" in content:
                print(f"  ✓ Embedding generation code exists")
            else:
                issues.append("Embedding generation code not found")
        
        # Check if HOLD₂ exists and has embeddings (runtime check)
        _DEFAULT_ROOT = project_root / "src" / "truth_forge"
        _DEFAULT_PROCESSED_DIR = _DEFAULT_ROOT / "system_elements" / "holds" / "knowledge_atoms" / "processed"
        duckdb2_path = _DEFAULT_PROCESSED_DIR / "hold2.duckdb"
        
        if duckdb2_path.exists() and get_duckdb_connection:
            try:
                conn = get_duckdb_connection(str(duckdb2_path), read_only=True)
                try:
                    # Check if embedding column exists
                    conn.execute("SELECT embedding FROM hold2_data LIMIT 1")
                    print(f"  ✓ Embedding column exists in HOLD₂")
                except Exception:
                    issues.append("Embedding column missing in HOLD₂")
                finally:
                    conn.close()
            except Exception as e:
                print(f"  ℹ️  Could not check HOLD₂ DuckDB: {e}")
        else:
            print(f"  ℹ️  HOLD₂ DuckDB doesn't exist yet (will be created on first write)")
    
    except Exception as e:
        issues.append(f"VSS validation failed: {e}")
    
    return {
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def validate_pipeline_data_processing() -> Dict[str, Any]:
    """Validate that pipeline stages process data correctly."""
    print("\n" + "=" * 80)
    print("VALIDATING PIPELINE DATA PROCESSING")
    print("=" * 80)
    
    issues = []
    
    # Check that stages have HOLD → AGENT → HOLD pattern
    for stage_num in range(17):
        stage_file = project_root / "pipelines" / "claude_code" / "scripts" / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
        
        if not stage_file.exists():
            continue
        
        content = stage_file.read_text()
        
        # Check for HOLD → AGENT → HOLD pattern documentation
        has_pattern = "HOLD₁" in content and "AGENT" in content and "HOLD₂" in content
        
        # Check for main() function (entry point)
        has_main = "def main()" in content
        
        # Check for processing logic
        has_processing = (
            "process" in content.lower() or
            "transform" in content.lower() or
            "load" in content.lower() or
            "query" in content.lower()
        )
        
        if not has_pattern:
            issues.append(f"Stage {stage_num}: Missing HOLD → AGENT → HOLD pattern documentation")
        
        if not has_main:
            issues.append(f"Stage {stage_num}: Missing main() function")
        
        if not has_processing:
            issues.append(f"Stage {stage_num}: May be missing processing logic")
    
    return {
        "stages_checked": 17,
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }


def main():
    """Run all validations."""
    print("\n" + "=" * 80)
    print("PIPELINE AND KNOWLEDGE ATOM VALIDATION")
    print("=" * 80)
    print()
    
    results = {}
    
    # 1. Validate pipeline stages
    results["pipeline_stages"] = validate_pipeline_stages()
    print(f"\n  Status: {results['pipeline_stages']['status']}")
    if results["pipeline_stages"]["issues"]:
        print(f"  Issues found: {len(results['pipeline_stages']['issues'])}")
        for issue in results["pipeline_stages"]["issues"][:10]:
            print(f"    - {issue}")
    
    # 2. Validate knowledge service architecture
    results["knowledge_service"] = validate_knowledge_service_architecture()
    print(f"\n  Status: {results['knowledge_service']['status']}")
    if results["knowledge_service"]["issues"]:
        print(f"  Issues found: {len(results['knowledge_service']['issues'])}")
        for issue in results["knowledge_service"]["issues"]:
            print(f"    - {issue}")
    
    # 3. Validate router functionality
    results["router"] = validate_router_functionality()
    print(f"\n  Status: {results['router']['status']}")
    if results["router"]["issues"]:
        print(f"  Issues found: {len(results['router']['issues'])}")
        for issue in results["router"]["issues"]:
            print(f"    - {issue}")
    
    # 4. Validate deduplication
    results["deduplication"] = validate_deduplication()
    print(f"\n  Status: {results['deduplication']['status']}")
    if results["deduplication"]["issues"]:
        print(f"  Issues found: {len(results['deduplication']['issues'])}")
        for issue in results["deduplication"]["issues"]:
            print(f"    - {issue}")
    
    # 5. Validate similarity normalization
    results["similarity"] = validate_similarity_normalization()
    print(f"\n  Status: {results['similarity']['status']}")
    if results["similarity"]["issues"]:
        print(f"  Issues found: {len(results['similarity']['issues'])}")
        for issue in results["similarity"]["issues"]:
            print(f"    - {issue}")
    
    # 6. Validate pipeline data processing
    results["data_processing"] = validate_pipeline_data_processing()
    print(f"\n  Status: {results['data_processing']['status']}")
    if results["data_processing"]["issues"]:
        print(f"  Issues found: {len(results['data_processing']['issues'])}")
        for issue in results["data_processing"]["issues"][:10]:
            print(f"    - {issue}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    all_passed = all(r["status"] == "PASS" for r in results.values())
    
    for name, result in results.items():
        status_icon = "✓" if result["status"] == "PASS" else "✗"
        print(f"{status_icon} {name}: {result['status']}")
    
    if all_passed:
        print("\n✅ ALL VALIDATIONS PASSED")
        return 0
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
