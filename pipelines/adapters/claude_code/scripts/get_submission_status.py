#!/usr/bin/env python3
"""Get detailed submission status for all stages."""
import json
from pathlib import Path
import re
from datetime import datetime
from collections import defaultdict

reviews_dir = Path('data/peer_reviews')
all_reviews = list(reviews_dir.glob('review_*.json'))

# Get reviews from last hour
cutoff_time = datetime.now().timestamp() - 3600
recent_reviews = [r for r in all_reviews if r.stat().st_mtime > cutoff_time]

stages = {}
for review_file in recent_reviews:
    try:
        with open(review_file, 'r') as f:
            data = json.load(f)
            
        object_path = data.get('object_path', '')
        stage_match = re.search(r'stage_(\d+)', object_path)
        if not stage_match:
            continue
        stage_num = int(stage_match.group(1))
        
        status = data.get('status', 'UNKNOWN')
        verdict = data.get('final_verdict', 'UNKNOWN')
        review_id = data.get('review_id', review_file.stem)
        
        # Count successful reviews
        models_completed = []
        if data.get('gemini_review', {}).get('success'):
            models_completed.append('gemini')
        if data.get('claude_review', {}).get('success'):
            models_completed.append('claude')
        if data.get('chatgpt_review', {}).get('success'):
            models_completed.append('chatgpt')
        
        review_count = f'{len(models_completed)}/3'
        
        # Get critical issues
        critical_issues = data.get('aggregated_critical_issues', [])
        if isinstance(critical_issues, list):
            critical_issues_count = len(critical_issues)
        else:
            critical_issues_count = critical_issues if isinstance(critical_issues, int) else 0
        
        # Only keep most recent per stage
        if stage_num not in stages or review_file.stat().st_mtime > stages[stage_num]['mtime']:
            stages[stage_num] = {
                'review_id': review_id,
                'status': status,
                'reviews': review_count,
                'models': ', '.join(models_completed) if models_completed else 'none',
                'verdict': verdict,
                'critical_issues': critical_issues_count,
                'mtime': review_file.stat().st_mtime
            }
    except Exception as e:
        continue

print('=' * 120)
print('PEER REVIEW SUBMISSION STATUS - THIRD ROUND')
print('=' * 120)
print(f'Recent reviews found: {len(recent_reviews)}')
print(f'Stages with reviews: {len(stages)}/17')
print()

# Status summary
status_counts = defaultdict(int)
verdict_counts = defaultdict(int)
for info in stages.values():
    status_counts[info['status']] += 1
    verdict_counts[info['verdict']] += 1

print('Status Breakdown:')
for status, count in sorted(status_counts.items()):
    icon = '✅' if status == 'COMPLETED' else '⚠️' if status == 'PARTIAL' else '❌'
    print(f'  {icon} {status}: {count}')

print()
print('Verdict Breakdown:')
for verdict, count in sorted(verdict_counts.items()):
    print(f'  {verdict}: {count}')

print()
print('=' * 120)
print(f'{'Stage':<8} {'Status':<20} {'Reviews':<10} {'Models':<25} {'Verdict':<20} {'Issues':<8} {'Review ID':<30}')
print('-' * 120)

for stage_num in sorted(stages.keys()):
    info = stages[stage_num]
    status_icon = '✅' if info['status'] == 'COMPLETED' else '⚠️' if info['status'] == 'PARTIAL' else '❌'
    print(f'{status_icon} {stage_num:<7} {info["status"]:<20} {info["reviews"]:<10} {info["models"][:23]:<25} {info["verdict"]:<20} {info["critical_issues"]:<8} {info["review_id"]:<30}')

print('-' * 120)

# Summary
completed = sum(1 for s in stages.values() if s['status'] == 'COMPLETED')
partial = sum(1 for s in stages.values() if s['status'] == 'PARTIAL')
needs_review = sum(1 for s in stages.values() if s['status'] == 'NEEDS_HUMAN_REVIEW')

print()
print(f'Summary:')
print(f'  ✅ COMPLETED: {completed}/17')
print(f'  ⚠️  PARTIAL: {partial}/17')
print(f'  ❌ NEEDS_HUMAN_REVIEW: {needs_review}/17')
print()

# Check for missing stages
missing = set(range(17)) - set(stages.keys())
if missing:
    print(f'⚠️  Stages not yet submitted: {sorted(missing)}')
else:
    print(f'✅ All 17 stages have been submitted!')

print()
