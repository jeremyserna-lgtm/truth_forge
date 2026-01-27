#!/usr/bin/env python3
"""Extract and summarize critical issues from peer reviews."""
import json
import re
from pathlib import Path
from collections import defaultdict

REVIEW_IDS = {
    6: "review:36d2561f5632d7a5",
    7: "review:62f1d84372be4b0f",
    8: "review:58f77dd1905fcdaa",
    9: "review:4ce652ac8709d481",
    10: "review:d30c1fcbb2d6554c",
}

project_root = Path(__file__).parent.parent.parent.parent
reviews_dir = project_root / "data" / "peer_reviews"

def extract_issues_by_category(review_data):
    """Extract issues grouped by category."""
    categories = defaultdict(list)
    
    for reviewer in ['gemini_review', 'claude_review', 'chatgpt_review']:
        review = review_data.get(reviewer)
        if not review or not review.get('success'):
            continue
        
        content = review.get('content', '').lower()
        
        # Categorize issues
        if 'memory' in content or 'oom' in content or 'exhaustion' in content or 'load.*into.*memory' in content:
            categories['memory'].append(reviewer.replace('_review', ''))
        if 'sql injection' in content or 'injection' in content:
            categories['sql_injection'].append(reviewer.replace('_review', ''))
        if 'error handling' in content or 'silent' in content or 'exception' in content:
            categories['error_handling'].append(reviewer.replace('_review', ''))
        if 'logic' in content or 'algorithm' in content or 'boundary' in content:
            categories['logic'].append(reviewer.replace('_review', ''))
        if 'stream' in content or 'batch' in content or 'scalability' in content:
            categories['scalability'].append(reviewer.replace('_review', ''))
    
    return categories

def main():
    """Extract critical issues summary."""
    print("="*80)
    print("CRITICAL ISSUES SUMMARY - STAGES 6-10")
    print("="*80)
    
    all_issues = {}
    
    for stage_num, review_id in REVIEW_IDS.items():
        review_file = reviews_dir / f"{review_id.replace('review:', 'review_')}.json"
        if not review_file.exists():
            continue
        
        with open(review_file, 'r') as f:
            data = json.load(f)
        
        categories = extract_issues_by_category(data)
        all_issues[stage_num] = {
            'verdict': data.get('final_verdict'),
            'status': data.get('status'),
            'categories': categories
        }
        
        print(f"\nStage {stage_num}: {data.get('final_verdict')} ({data.get('status')})")
        print("-" * 40)
        for category, reviewers in categories.items():
            print(f"  {category}: {len(set(reviewers))} reviewers flagged")
    
    # Summary
    print("\n" + "="*80)
    print("ISSUE FREQUENCY ACROSS ALL STAGES")
    print("="*80)
    
    category_counts = defaultdict(int)
    for stage_data in all_issues.values():
        for category in stage_data['categories'].keys():
            category_counts[category] += 1
    
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"{category}: {count}/5 stages")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
