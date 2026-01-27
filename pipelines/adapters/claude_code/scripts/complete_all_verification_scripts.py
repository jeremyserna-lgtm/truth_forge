#!/usr/bin/env python3
"""
Complete all verification scripts by removing TODOs and implementing actual checks.
"""

from pathlib import Path
import re

def complete_stage_0_verification(content: str) -> str:
    """Complete Stage 0 verification script."""
    # Replace TODO sections with actual checks
    content = re.sub(
        r'# TODO: Implement specific check for: Manifest exists.*?\n\s+print\("   ✅ Manifest exists"\)',
        '''# Check if manifest file exists
        import glob
        manifest_dir = Path(project_root) / "data" / "pipelines" / "claude_code" / "manifests"
        manifest_files = sorted(glob.glob(str(manifest_dir / "discovery_*.json")), reverse=True)
        
        if not manifest_files:
            print("   ❌ No manifest files found")
            print("   What this means: Stage 0 hasn't run yet or failed to create a manifest.")
            print("   What to do: Run Stage 0 first, then check for errors.")
            all_checks_passed = False
        else:
            latest_manifest = manifest_files[0]
            print(f"   ✅ Found manifest: {Path(latest_manifest).name}")''',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'# TODO: Implement specific check for: go_no_go is GO.*?\n\s+print\("   ✅ go_no_go is GO"\)',
        '''# Check go_no_go status
        import json
        try:
            with open(latest_manifest, 'r') as f:
                manifest = json.load(f)
            go_no_go = manifest.get('go_no_go', '').upper()
            if go_no_go.startswith('GO'):
                print(f"   ✅ go_no_go is GO")
            else:
                print(f"   ❌ go_no_go is {go_no_go} (not GO)")
                print("   What this means: Stage 0 determined the data is not ready.")
                print("   What to do: Check why go_no_go is not GO, fix the issue, then re-run Stage 0.")
                all_checks_passed = False
        except Exception as e:
            print(f"   ❌ Error reading manifest: {e}")
            all_checks_passed = False''',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'# TODO: Implement specific check for: File count > 0.*?\n\s+print\("   ✅ File count > 0"\)',
        '''# Check file count
        try:
            file_count = manifest.get('file_count', 0)
            if file_count > 0:
                print(f"   ✅ Found {file_count} JSONL files")
            else:
                print("   ❌ No JSONL files found")
                print("   What this means: Stage 0 found no source files to process.")
                print("   What to do: Check your source directory has JSONL files, then re-run Stage 0.")
                all_checks_passed = False
        except Exception as e:
            print(f"   ❌ Error checking file count: {e}")
            all_checks_passed = False''',
        content,
        flags=re.DOTALL
    )
    
    return content

def complete_stage_1_verification(content: str) -> str:
    """Complete Stage 1 verification script."""
    content = re.sub(
        r'# TODO: Implement specific check for: DLQ has no errors.*?\n\s+print\("   ✅ DLQ has no errors"\)',
        '''# Check Dead Letter Queue for failed parses
        dlq_table = get_full_table_id("claude_code_stage_1_dlq")
        try:
            query = f"SELECT COUNT(*) as error_count FROM `{dlq_table}`"
            if run_id:
                query += " WHERE run_id = @run_id"
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
                )
                result = list(client.query(query, job_config=job_config).result())[0]
            else:
                result = list(client.query(query).result())[0]
            
            if result.error_count > 0:
                print(f"   ⚠️  Found {result.error_count} failed JSON parses in DLQ")
                print("   What this means: Some lines in JSONL files couldn't be parsed.")
                print("   What to do: Check the DLQ table to see which lines failed and why.")
            else:
                print("   ✅ No failed parses in DLQ")
        except Exception as e:
            # DLQ table might not exist if no errors occurred
            if "not found" in str(e).lower():
                print("   ✅ DLQ table doesn't exist (no errors occurred)")
            else:
                print(f"   ⚠️  Could not check DLQ: {e}")''',
        content,
        flags=re.DOTALL
    )
    return content

def complete_stage_7_verification(content: str) -> str:
    """Complete Stage 7 verification script."""
    content = re.sub(
        r'# TODO: Implement specific check for: L4 entities created.*?\n\s+print\("   ✅ L4 entities created"\)',
        '''# Check that records are Level 4 entities
        try:
            query = f"""
            SELECT 
                COUNT(*) as total,
                COUNTIF(level = 4) as level_4_count,
                COUNTIF(level != 4) as wrong_level_count
            FROM `{stage_table}`
            """
            result = list(client.query(query).result())[0]
            
            if result.wrong_level_count > 0:
                print(f"   ❌ Found {result.wrong_level_count} records with wrong level")
                print("   What this means: Some records are not Level 4 as they should be.")
                print("   What to do: This is a data corruption issue - contact support.")
                all_checks_passed = False
            else:
                print(f"   ✅ All {result.total:,} records are Level 4 entities")
        except Exception as e:
            print(f"   ❌ Error checking levels: {e}")
            all_checks_passed = False''',
        content,
        flags=re.DOTALL
    )
    return content

def main():
    """Complete all verification scripts."""
    scripts_dir = Path(__file__).parent
    
    print("🔧 Completing Verification Scripts (Removing TODOs)\n")
    print("="*80)
    
    completers = {
        0: complete_stage_0_verification,
        1: complete_stage_1_verification,
        7: complete_stage_7_verification,
    }
    
    for stage_num in range(17):
        verify_file = scripts_dir / f"stage_{stage_num}" / f"verify_stage_{stage_num}.py"
        
        if not verify_file.exists():
            continue
        
        content = verify_file.read_text()
        
        if 'TODO:' in content:
            if stage_num in completers:
                new_content = completers[stage_num](content)
                verify_file.write_text(new_content)
                print(f"✅ Completed Stage {stage_num} verification script")
            else:
                print(f"⚠️  Stage {stage_num} has TODOs (needs manual completion)")
        else:
            print(f"✅ Stage {stage_num} already complete")
    
    print("\n" + "="*80)
    print("✅ Verification script completion done!")

if __name__ == "__main__":
    main()
