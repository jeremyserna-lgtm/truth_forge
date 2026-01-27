#!/usr/bin/env python3
"""Fix all trust reports to use rollback scripts instead of command-line."""
from pathlib import Path
import re

def fix_trust_report(stage_num: int):
    """Fix a single trust report."""
    stage_dir = Path(__file__).parent / f"stage_{stage_num}"
    trust_report = stage_dir / "TRUST_REPORT.md"
    
    if not trust_report.exists():
        return False
    
    content = trust_report.read_text()
    original = content
    
    # Replace bq query commands with verification script
    content = re.sub(
        r'```bash\s*bq query[^`]*```',
        '```bash\npython3 pipelines/claude_code/scripts/stage_' + str(stage_num) + '/verify_stage_' + str(stage_num) + '.py [--run-id RUN_ID]\n```',
        content,
        flags=re.DOTALL
    )
    
    # Replace rollback section
    rollback_pattern = r'## How to Rollback.*?(?=##|\Z)'
    new_rollback = f"""## How to Rollback

### If Stage {stage_num} Causes Problems:

**Easy Rollback (No Coding Required):**

Simply run the rollback script:
```bash
python3 pipelines/claude_code/scripts/stage_{stage_num}/rollback_stage_{stage_num}.py --run-id YOUR_RUN_ID
```

The script will:
1. Show you how many records will be deleted
2. Ask for confirmation (type 'yes' to confirm)
3. Delete all Stage {stage_num} data for that run_id
4. Give you clear feedback about what happened

**What this means**: All data created by Stage {stage_num} for that specific run will be removed.

**What to do**: After rollback, you can re-run Stage {stage_num} if needed.

**Note**: You don't need to know SQL or use command-line tools. Just run the script and follow the prompts.
"""
    
    content = re.sub(rollback_pattern, new_rollback, content, flags=re.DOTALL)
    
    # Remove git checkout commands
    content = re.sub(r'```bash\s*git checkout[^`]*```', '', content)
    
    # Replace any remaining bq commands in "How to Test" sections
    content = re.sub(
        r'bq query[^\n]*',
        'python3 pipelines/claude_code/scripts/stage_' + str(stage_num) + '/verify_stage_' + str(stage_num) + '.py',
        content
    )
    
    if content != original:
        trust_report.write_text(content)
        return True
    return False

def main():
    """Fix all trust reports."""
    scripts_dir = Path(__file__).parent
    
    print("Fixing all trust reports...")
    fixed_count = 0
    
    for stage_num in range(17):
        if fix_trust_report(stage_num):
            print(f"  ✅ Stage {stage_num}: Fixed")
            fixed_count += 1
        else:
            print(f"  ℹ️  Stage {stage_num}: No changes needed or file missing")
    
    print(f"\n✅ Fixed {fixed_count} trust reports!")

if __name__ == "__main__":
    main()
