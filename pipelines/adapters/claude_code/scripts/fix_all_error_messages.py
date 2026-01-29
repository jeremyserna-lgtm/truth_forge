#!/usr/bin/env python3
"""Fix all technical error messages to be user-friendly."""
from __future__ import annotations

import re
import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent

# Stage-specific error message mappings
STAGE_ERROR_MESSAGES = {
    1: "Failed to extract data from source files",
    2: "Failed to clean and deduplicate extracted data",
    3: "Failed to generate entity identities",
    4: "Failed to stage data for SPINE processing",
    5: "Failed to tokenize messages",
    6: "Failed to detect sentences",
    7: "Failed to create message entities",
    8: "Failed to create conversation entities",
    9: "Failed to generate embeddings",
    10: "Failed to extract information using LLM",
    11: "Failed to analyze sentiment",
    12: "Failed to extract topics",
    13: "Failed to build entity relationships",
    14: "Failed to aggregate entity data",
    15: "Failed to validate entities",
}

BATCH_ERROR_MESSAGES = {
    "Embedding batch failed": "Failed to generate embeddings for a batch of messages",
    "Sentiment batch failed": "Failed to analyze sentiment for a batch of messages",
    "MERGE failed": "Unable to merge records, using direct insert instead",
}

def fix_stage_error_messages(stage_num: int) -> bool:
    """Fix error messages in a stage file."""
    stage_file = scripts_dir / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
    
    if not stage_file.exists():
        return False
    
    content = stage_file.read_text(encoding="utf-8")
    original = content
    
    # Fix main stage error handler
    stage_error_pattern = rf'logger\.error\(f"Stage {stage_num} failed: \{{e\}}", exc_info=True'
    if stage_num in STAGE_ERROR_MESSAGES:
        user_message = STAGE_ERROR_MESSAGES[stage_num]
        replacement = f'''logger.error("{user_message}")
            logger.error(f"Error: {{str(e)}}")
            logger.debug(f"Technical details: {{e}}", exc_info=True)'''
        content = re.sub(stage_error_pattern, replacement, content)
    
    # Fix batch processing errors
    for old_msg, new_msg in BATCH_ERROR_MESSAGES.items():
        # Pattern: logger.error(f"Embedding batch failed: {e}")
        pattern = rf'logger\.error\(f"{re.escape(old_msg)}: \{{e\}}"\)'
        replacement = f'''logger.error("{new_msg}")
            logger.debug(f"Technical details: {{e}}", exc_info=True)'''
        content = re.sub(pattern, replacement, content)
    
    # Fix other technical error patterns
    # Pattern: logger.error(f"Failed to load spaCy model: {e}")
    content = re.sub(
        r'logger\.error\(f"Failed to load spaCy model: \{e\}"\)',
        'logger.error("Failed to load language processing model")\n            logger.debug(f"Technical details: {e}", exc_info=True)',
        content
    )
    
    # Fix MERGE failed messages (already handled but ensure consistency)
    content = re.sub(
        r'logger\.error\(f"MERGE failed, using direct insert: \{e\}"\)',
        'logger.warning("Unable to merge records, using direct insert instead")\n            logger.debug(f"MERGE failed: {e}", exc_info=True)',
        content
    )
    
    if content != original:
        stage_file.write_text(content, encoding="utf-8")
        print(f"✅ Fixed Stage {stage_num} error messages")
        return True
    
    return False

def main():
    """Fix all stage error messages."""
    stages_to_fix = list(range(1, 17))  # Stages 1-16
    
    fixed = 0
    for stage_num in stages_to_fix:
        if fix_stage_error_messages(stage_num):
            fixed += 1
    
    print(f"\n{'=' * 80}")
    print(f"Fixed {fixed} stage(s)")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
