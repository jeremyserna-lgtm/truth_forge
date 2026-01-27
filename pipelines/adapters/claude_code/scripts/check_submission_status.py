#!/usr/bin/env python3
"""Check status of peer review submissions."""
import json
from pathlib import Path
import re
from collections import defaultdict

reviews_dir = Path('data/peer_reviews')
all_reviews = list(reviews_dir.glob('review_*.json'))

# Get most recent reviews (last hour)
from datetime import datetime, timedelta
cutoff_time = datetime.now().timestamp() - 3600  # Last hour

recent_reviews = [r for r in all_reviews if r.stat().st_mtime > cutoff_time]

stages = {}
for review_file in recent_reviews:
    try:
        with open(review_file, 'r') as f:
            data = json.load(f)
            
        # Get stage number from object_path
        object_path = data.get('object_path', '') or str(data.get('object', {}))
        stage_match = re.search(r'stage_(\d+)', object_path)
        
        if not stage_match:
            continue
            
        stage_num = int(stage_match.group(1))
        
        # Get status
        status = data.get('status', 'UNKNOWN')
        if isinstance(status, dict):
            status = status.get('value', status.get('status', 'UNKNOWN'))
        
        # Get reviews
        successful_reviews = data.get('successful_reviews', [])
        all_reviews_list = data.get('all_reviews', [])
        successful_count = len(successful_reviews) if isinstance(successful_reviews, list) else 0
        total_count = len(all_reviews_list) if isinstance(all_reviews_list, list) else 0
        
        # Get verdict
        verdict = data.get('final_verdict', 'UNKNOWN')
        if isinstance(verdict, dict):
            verdict = verdict.get('value', verdict.get('verdict', 'UNKNOWN'))
        
        review_id = data.get('review_id', review_file.stem)
        
        # Count critical issues
        critical_issues = 0
        if 'critical_issues' in data:
            if isinstance(data['critical_issues'], list):
                critical_issues = len(data['critical_issues'])
            elif isinstance(data['critical_issues'], int):
                critical_issues = data['critical_issues']
        
        # Get models that completed
        models = []
        if isinstance(successful_reviews, list):
            for review in successful_reviews:
                if isinstance(review, dict):
                    model = review.get('model', {})
                    if isinstance(model, dict):
                        models.append(model.get('value', 'unknown'))
                    else:
                        models.append(str(model))
        
        # Only keep most recent review per stage
        if stage_num not in stages or review_file.stat().st_mtime > stages[stage_num]['mtime']:
            stages[stage_num] = {
                'review_id': review_id,
                'status': status,
                'reviews': f'{successful_count}/{total_count}',
                'verdict': verdict,
                'critical_issues': critical_issues,
                'models': ', '.join(models) if models else 'none',
                'mtime': review_file.stat().st_mtime
            }
    except Exception as e:
        continue

# Summary
print('=' * 120)
print('PEER REVIEW SUBMISSION STATUS')
print('=' * 120)
print(f'Recent reviews found: {len(recent_reviews)}')
print(f'Stages with reviews: {len(stages)}/17')
print()

# Status breakdown
status_counts = defaultdict(int)
verdict_counts = defaultdict(int)
for info in stages.values():
    status_counts[info['status']] += 1
    verdict_counts[info['verdict']] += 1

print('Status Breakdown:')
for status, count in sorted(status_counts.items()):
    print(f'  {status}: {count}')

print()
print('Verdict Breakdown:')
for verdict, count in sorted(verdict_counts.items()):
    print(f'  {verdict}: {count}')

print()
print('=' * 120)
print(f'{'Stage':<8} {'Status':<20} {'Reviews':<10} {'Verdict':<20} {'Issues':<8} {'Models':<20} {'Review ID':<30}')
print('-' * 120)

for stage_num in sorted(stages.keys()):
    info = stages[stage_num]
    status_icon = '✅' if info['status'] == 'COMPLETED' else '⚠️' if info['status'] == 'PARTIAL' else '🔄' if 'PROCESSING' in info['status'] else '❌'
    print(f'{status_icon} {stage_num:<7} {info["status"]:<20} {info["reviews"]:<10} {info["verdict"]:<20} {info["critical_issues"]:<8} {info["models"][:18]:<20} {info["review_id"]:<30}')

print('-' * 120)

# Missing stages
missing = set(range(17)) - set(stages.keys())
if missing:
    print(f'\n⚠️  Stages not yet submitted: {sorted(missing)}')
else:
    print(f'\n✅ All 17 stages have been submitted!')

print()
