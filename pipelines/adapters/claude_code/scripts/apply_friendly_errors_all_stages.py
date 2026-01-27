#!/usr/bin/env python3
"""
Apply non-coder friendly error messages to all pipeline stages.

This script finds common error patterns and makes them friendly.
"""

import re
from pathlib import Path
from typing import List, Tuple

def make_validation_error_friendly(content: str, stage_num: int) -> Tuple[str, List[str]]:
    """Make ValidationError messages friendly."""
    changes = []
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Pattern 1: raise ValidationError("simple message")
        match = re.search(r'raise ValidationError\(["\']([^"\']+)["\']\)', line)
        if match and 'What this means' not in '\n'.join(lines[max(0, i-5):i+10]):
            error_msg = match.group(1)
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Generate friendly message based on error content
            if 'no' in error_msg.lower() and ('stage' in error_msg.lower() or 'run' in error_msg.lower()):
                friendly = f'''{indent_str}error_msg = (
{indent_str}    "❌ VALIDATION FAILED: {error_msg}\\n"
{indent_str}    "\\nWhat this means: Stage {stage_num} needs data from an upstream stage that hasn't run yet.\\n"
{indent_str}    "Without this data, Stage {stage_num} cannot process anything.\\n"
{indent_str}    "\\nWhat to do:\\n"
{indent_str}    "  1. Run the upstream stages first\\n"
{indent_str}    "  2. Wait for them to complete successfully\\n"
{indent_str}    "  3. Then run Stage {stage_num} again"
{indent_str})
{indent_str}raise ValidationError(error_msg)'''
                new_lines.append(friendly)
                changes.append(f"Line {i+1}: Made ValidationError friendly")
                i += 1
                continue
            elif 'NULL' in error_msg or 'null' in error_msg:
                friendly = f'''{indent_str}error_msg = (
{indent_str}    "❌ VALIDATION FAILED: {error_msg}\\n"
{indent_str}    "\\nWhat this means: Some records are missing required information.\\n"
{indent_str}    "This will cause Stage {stage_num} to fail because it needs complete data.\\n"
{indent_str}    "\\nWhat to do:\\n"
{indent_str}    "  1. Check the upstream stage output\\n"
{indent_str}    "  2. Fix the data quality issues\\n"
{indent_str}    "  3. Re-run the upstream stage, then try Stage {stage_num} again"
{indent_str})
{indent_str}raise ValidationError(error_msg)'''
                new_lines.append(friendly)
                changes.append(f"Line {i+1}: Made ValidationError friendly")
                i += 1
                continue
        
        # Pattern 2: raise ValidationError(f"message with {variable}")
        match = re.search(r'raise ValidationError\(\s*f?["\']([^"\']*\{[^}]*\}[^"\']*)["\']', line)
        if match and 'What this means' not in '\n'.join(lines[max(0, i-5):i+10]):
            # Check if next line completes it
            if i + 1 < len(lines) and ')' in lines[i+1]:
                error_template = match.group(1)
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                friendly = f'''{indent_str}error_msg = (
{indent_str}    f"❌ VALIDATION FAILED: {error_template}\\n"
{indent_str}    "\\nWhat this means: Some records are missing required information.\\n"
{indent_str}    f"This will cause Stage {stage_num} to fail because it needs complete data.\\n"
{indent_str}    "\\nWhat to do:\\n"
{indent_str}    "  1. Check the upstream stage output\\n"
{indent_str}    "  2. Fix the data quality issues\\n"
{indent_str}    "  3. Re-run the upstream stage, then try Stage {stage_num} again"
{indent_str})
{indent_str}raise ValidationError(error_msg)'''
                new_lines.append(friendly)
                # Skip the next line if it's just the closing paren
                if i + 1 < len(lines) and lines[i+1].strip() == ')':
                    i += 2
                else:
                    i += 1
                changes.append(f"Line {i+1}: Made ValidationError friendly")
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines), changes

def make_runtime_error_friendly(content: str, stage_num: int) -> Tuple[str, List[str]]:
    """Make RuntimeError messages friendly."""
    changes = []
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Pattern: raise RuntimeError(f"message")
        if 'raise RuntimeError' in line and 'friendly_error' not in '\n'.join(lines[max(0, i-10):i+5]):
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Check if it's a knowledge atom error
            if 'knowledge atom' in line.lower() or 'Knowledge atom' in line:
                friendly = f'''{indent_str}# Non-coder friendly error message
{indent_str}friendly_error = (
{indent_str}    f"❌ CRITICAL ERROR: Failed to save audit trail information\\n"
{indent_str}    f"\\nWhat this means: Stage {stage_num} completed but couldn't record what it did.\\n"
{indent_str}    f"This is a critical failure because the system needs to track all operations.\\n"
{indent_str}    f"\\nWhat to do:\\n"
{indent_str}    f"  1. Check the error details in the logs above\\n"
{indent_str}    f"  2. Check if the knowledge atom system is working\\n"
{indent_str}    f"  3. Fix the problem, then re-run Stage {stage_num}\\n"
{indent_str}    f"\\nTechnical error: {{str(e)}}"
{indent_str})
{indent_str}print(friendly_error)'''
                new_lines.append(friendly)
                new_lines.append(line)  # Keep original raise
                changes.append(f"Line {i+1}: Added friendly RuntimeError message")
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines), changes

def main():
    """Apply friendly error messages to all stages."""
    scripts_dir = Path(__file__).parent
    
    print("🔧 Applying Friendly Error Messages to All Stages\n")
    print("="*80)
    
    all_changes = {}
    
    for stage_num in range(17):
        stage_file = scripts_dir / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
        
        if not stage_file.exists():
            continue
        
        print(f"\nProcessing Stage {stage_num}...")
        content = stage_file.read_text()
        original = content
        
        # Apply fixes
        content, validation_changes = make_validation_error_friendly(content, stage_num)
        content, runtime_changes = make_runtime_error_friendly(content, stage_num)
        
        all_changes_list = validation_changes + runtime_changes
        
        if all_changes_list:
            stage_file.write_text(content)
            all_changes[stage_num] = all_changes_list
            print(f"  ✅ Applied {len(all_changes_list)} friendly error message(s)")
        else:
            print(f"  ✅ Already has friendly error messages (or no errors to fix)")
    
    print("\n" + "="*80)
    if all_changes:
        print(f"\n✅ Applied friendly error messages to {len(all_changes)} stages")
        for stage, changes in all_changes.items():
            print(f"  Stage {stage}: {len(changes)} change(s)")
    else:
        print("\n✅ All stages already have friendly error messages!")
    
    return all_changes

if __name__ == "__main__":
    main()
