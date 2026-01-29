#!/usr/bin/env python3
"""
Inventory all Cursor chat sessions to identify agent types and volumes.

This script scans Cursor's workspaceStorage to find all conversation data,
categorize by agent type (Cursor Native, GitHub Copilot, Claude Code, etc.),
and provides statistics for extraction planning.
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def inventory_cursor_chats():
    """Scan all Cursor workspaces and inventory conversation data."""
    
    base = Path.home() / 'Library/Application Support/Cursor/User/workspaceStorage'
    
    if not base.exists():
        print(f"ERROR: Cursor workspaceStorage not found at: {base}")
        return
    
    stats = defaultdict(lambda: {
        'count': 0,
        'total_requests': 0, 
        'size_mb': 0,
        'files': []
    })
    
    total_files = 0
    total_size = 0
    
    print("Scanning Cursor workspaces...")
    print()
    
    for workspace in base.iterdir():
        if not workspace.is_dir():
            continue
            
        chat_dir = workspace / 'chatSessions'
        if not chat_dir.exists():
            continue
        
        workspace_name = workspace.name
        
        for json_file in chat_dir.glob('*.json'):
            total_files += 1
            size_mb = json_file.stat().st_size / 1024 / 1024
            total_size += size_mb
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                session_id = data.get('sessionId', 'unknown')
                requests = data.get('requests', [])
                
                if not requests:
                    agent_type = 'Empty/No Requests'
                else:
                    # Check first request for agent type
                    first_req = requests[0]
                    agent = first_req.get('agent', {})
                    responder = first_req.get('responderUsername', '')
                    
                    # Identify agent type
                    if agent.get('extensionDisplayName'):
                        agent_type = agent.get('extensionDisplayName')
                    elif 'Claude' in responder:
                        agent_type = 'Claude Code (detected)'
                    elif responder:
                        agent_type = f'Unknown ({responder})'
                    else:
                        agent_type = 'Cursor Native'
                
                stats[agent_type]['count'] += 1
                stats[agent_type]['total_requests'] += len(requests)
                stats[agent_type]['size_mb'] += size_mb
                stats[agent_type]['files'].append({
                    'workspace': workspace_name,
                    'file': json_file.name,
                    'session_id': session_id,
                    'requests': len(requests),
                    'size_mb': size_mb
                })
                
            except json.JSONDecodeError as e:
                print(f'  JSON Error in {json_file.name}: {e}')
                stats['JSON Parse Error']['count'] += 1
                stats['JSON Parse Error']['size_mb'] += size_mb
            except Exception as e:
                print(f'  Error reading {json_file.name}: {e}')
                stats['Read Error']['count'] += 1
                stats['Read Error']['size_mb'] += size_mb
    
    # Print results
    print('=' * 90)
    print('CURSOR CHAT INVENTORY')
    print('=' * 90)
    print()
    print(f'Total Files Scanned: {total_files}')
    print(f'Total Size: {total_size:.1f} MB ({total_size/1024:.2f} GB)')
    print()
    print('=' * 90)
    print(f'{"Agent Type":40s} | {"Files":>6s} | {"Requests":>10s} | {"Size (MB)":>10s}')
    print('=' * 90)
    
    for agent_type in sorted(stats.keys(), key=lambda x: stats[x]['size_mb'], reverse=True):
        data = stats[agent_type]
        print(f'{agent_type:40s} | {data["count"]:6d} | {data["total_requests"]:10d} | {data["size_mb"]:10.1f}')
    
    print('=' * 90)
    print()
    
    # Show largest files for each agent type with Claude
    claude_types = [t for t in stats.keys() if 'Claude' in t or 'claude' in t.lower()]
    
    if claude_types:
        print('CLAUDE CODE CONVERSATIONS (Top 10 largest):')
        print('=' * 90)
        print(f'{"Workspace":35s} | {"File":36s} | {"Reqs":>6s} | {"MB":>8s}')
        print('-' * 90)
        
        all_claude_files = []
        for agent_type in claude_types:
            all_claude_files.extend(stats[agent_type]['files'])
        
        # Sort by size
        all_claude_files.sort(key=lambda x: x['size_mb'], reverse=True)
        
        for file_info in all_claude_files[:10]:
            print(f'{file_info["workspace"][:35]:35s} | '
                  f'{file_info["file"]:36s} | '
                  f'{file_info["requests"]:6d} | '
                  f'{file_info["size_mb"]:8.1f}')
        
        total_claude_requests = sum(stats[t]['total_requests'] for t in claude_types)
        total_claude_size = sum(stats[t]['size_mb'] for t in claude_types)
        
        print('=' * 90)
        print(f'Total Claude Conversations: {sum(stats[t]["count"] for t in claude_types)} files')
        print(f'Total Claude Requests: {total_claude_requests:,}')
        print(f'Total Claude Size: {total_claude_size:.1f} MB')
        print()
    else:
        print('⚠️  NO CLAUDE CODE CONVERSATIONS FOUND')
        print('The Cursor chat data appears to be primarily GitHub Copilot.')
        print()
    
    return stats

if __name__ == '__main__':
    try:
        stats = inventory_cursor_chats()
    except KeyboardInterrupt:
        print('\n\nInventory interrupted by user.')
    except Exception as e:
        print(f'\n\nFATAL ERROR: {e}')
        import traceback
        traceback.print_exc()
