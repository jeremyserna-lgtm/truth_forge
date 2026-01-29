# COMPLETE Cursor Data Analysis & Extraction Plan

**Discovery**: Found massive conversation data in Cursor workspaceStorage  
**Total Size**: ~1+ GB of conversation JSON files across 9 workspaces  
**Sources Found**: GitHub Copilot, Cursor Native agents

---

## What We Found

### Cursor chatSessions Data
**Location**: `~/Library/Application Support/Cursor/User/workspaceStorage/*/chatSessions/*.json`

**Largest Files** (Top conversationsconfidence):
| Size | Workspace | File | Agent Type |
|------|-----------|------|------------|
| 200MB | f794878dd35b5b11f87a3c3d51e4ec96 | 971763e9-b1b7-4043-92d7-41e0f35d6d85.json | Unknown |
| 147MB | f794878dd35b5b11f87a3c3d51e4ec96 | 49f75bb7-7ebb-4387-a658-219f45c0a9e7.json | Unknown |
| 91MB | Multiple workspaces | dbac012c-34a4-42d1-858f-0ca846a20d28.json | Unknown |
| 80MB | Multiple workspaces | 10a88d23-c918-463c-a801-40018b5f02aa.json | GitHub Copilot ✅ |
| 74MB | f794878dd35b5b11f87a3c3d51e4ec96 | 1751c853-97c5-4b09-9a3c-0be6285c9d4f.json | Unknown |

**Total**: 1+ GB of conversation data (need full inventory)

---

## Agent Types in Cursor

According to CURSOR_CHAT_STORAGE_COMPLETE.md:

1. **Cursor Agents** (native) - Agent field missing/empty
2. **GitHub Copilot** - `agent.extensionDisplayName = "GitHub Copilot Chat"`
3. **Claude Code** - `agent.extensionDisplayName = "Claude Code"` ← WHAT WE WANT

---

## Extraction Strategy

### Phase 1: Full Inventory (IMMEDIATE)
Create script to:
1. Scan all workspaces
2. Parse each JSON file
3. Identify agent type from structure
4. Count messages per agent type
5. Extract date ranges

### Phase 2: Filter for Claude Code  
Extract only conversations where:
- `agent.extensionDisplayName = "Claude Code"`  
- OR `responderUsername` contains "Claude"

### Phase 3: Process to Pipeline
- Convert to same JSONL format as `claude_code_stage_3`
- Compare dates to verify overlap/gap
- Add to pipeline

---

## Critical Questions to Answer

### 1. Is This the Source of claude_code_stage_3?
**Hypothesis**: The 227K messages in `claude_code_stage_3` came from Cursor chatSessions

**To verify**:
- Compare dates (Cursor vs stage_3)
- stage_3 dates: Oct 2025 → Jan 2026
- Check if Cursor files have similar dates

### 2. How Much is Claude vs Copilot?
Need to analyze agent types:
- GitHub Copilot conversations (confirmed exists)
- Claude Code conversations (searching for)
- Cursor Native conversations

### 3. Do We Need This Data?
**If Cursor = Source of stage_3**: Already have it, just continue pipeline  
**If Cursor ≠ Source**: Need to extract Claude conversations separately

---

## Next Steps (Right Now)

### 1. Create Inventory Script
```python
#!/usr/bin/env python3
"""Inventory all Cursor chat sessions."""

import json
import os
from pathlib import Path
from collections import defaultdict

def inventory_cursor_chats():
    base = Path.home() / 'Library/Application Support/Cursor/User/workspaceStorage'
    
    stats = defaultdict(lambda: {'count': 0, 'total_requests': 0, 'size_mb': 0})
    
    for workspace in base.iterdir():
        chat_dir = workspace / 'chatSessions'
        if not chat_dir.exists():
            continue
            
        for json_file in chat_dir.glob('*.json'):
            size_mb = json_file.stat().st_size / 1024 / 1024
            
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                requests = data.get('requests', [])
                if not requests:
                    agent_type = 'Empty'
                else:
                    agent = requests[0].get('agent', {})
                    agent_type = agent.get('extensionDisplayName', 'Cursor Native')
                
                stats[agent_type]['count'] += 1
                stats[agent_type]['total_requests'] += len(requests)
                stats[agent_type]['size_mb'] += size_mb
                
            except Exception as e:
                print(f'Error reading {json_file}: {e}')
                stats['Error']['count'] += 1
    
    # Print results
    print('Cursor Chat Inventory:')
    print('=' * 80)
    for agent_type, data in sorted(stats.items()):
        print(f'{agent_type:30s} | {data["count"]:3d} files | '
              f'{data["total_requests"]:6d} requests | {data["size_mb"]:.1f} MB')

if __name__ == '__main__':
    inventory_cursor_chats()
```

### 2. Run Inventory
```bash
cd /Users/jeremyserna/truth_forge/training
python3 cursor_inventory.py
```

### 3. Based on Results, Decide:
- Extract Claude Code conversations
- Compare with claude_code_stage_3
- Determine if separate data source

---

## Integration with Genesis Training

### If Cursor Has Significant Claude Data

**Add as Source 3**:
- ChatGPT/Clara: 53,697 messages (emotional processing)
- Claude Code (primary): 226,972 messages (transformation)
- Cursor Claude: TBD messages (October transition) ← Could be THE GAP

**Timeline filled**:
- Aug 2024 - Nov 2025: ChatGPT  
- Oct 2024: Cursor/Claude transition
- Oct 2025 - Jan 2026: Claude Code primary

### If Cursor = Source of stage_3

**No additional work needed**:
- Data already in pipeline
- Continue processing stage_3
- Cursor was just the storage format

---

## Immediate Action

1. **Create & run inventory script** (5 minutes)
2. **Analyze results** - How much Claude vs Copilot?
3. **Sample Claude conversations** - Check content, dates
4. **Compare with stage_3** - Same source or different?
5. **Decision**: Extract separately or continue stage_3?

---

**Bottom Line**: Found 1+ GB of Cursor conversation data. Need to inventory it to determine:
1. How much is Claude Code vs Copilot?
2. Is this the source of existing stage_3 data?
3. Does it fill the October transition gap?

Creating inventory script now...
