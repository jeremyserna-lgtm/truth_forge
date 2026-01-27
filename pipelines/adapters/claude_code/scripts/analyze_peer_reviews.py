#!/usr/bin/env python3
"""Analyze peer review results and extract critical issues."""
import json
import sys
from pathlib import Path

# Review IDs for stages 6-10
REVIEW_IDS = {
    6: "review:36d2561f5632d7a5",
    7: "review:62f1d84372be4b0f",
    8: "review:58f77dd1905fcdaa",
    9: "review:4ce652ac8709d481",
    10: "review:d30c1fcbb2d6554c",  # Updated from earlier
}

project_root = Path(__file__).parent.parent.parent.parent
reviews_dir = project_root / "data" / "peer_reviews"

def extract_critical_issues(review_data):
    """Extract critical issues from review data."""
    issues = []
    
    # Check each reviewer's response
    for reviewer in ['gemini_review', 'claude_review', 'chatgpt_review']:
        review = review_data.get(reviewer)
        if not review or not review.get('success'):
            continue
        
        content = review.get('content', '')
        
        # Try to extract structured issues
        # Look for patterns like "Critical Issue:", "Issue:", "Problem:", etc.
        lines = content.split('\n')
        current_issue = None
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_issue:
                    issues.append(current_issue)
                    current_issue = None
                continue
            
            # Check if this looks like an issue header
            if any(marker in line.lower() for marker in ['critical issue', 'issue:', 'problem:', 'vulnerability', 'bug:', 'error:']):
                if current_issue:
                    issues.append(current_issue)
                current_issue = {'type': reviewer.replace('_review', ''), 'text': line}
            elif current_issue:
                current_issue['text'] += ' ' + line
            elif 'sql injection' in line.lower() or 'memory' in line.lower() or 'security' in line.lower() or 'error handling' in line.lower():
                issues.append({'type': reviewer.replace('_review', ''), 'text': line})
    
    if current_issue:
        issues.append(current_issue)
    
    return issues

def analyze_review(stage_num):
    """Analyze a single review."""
    review_id = REVIEW_IDS.get(stage_num)
    if not review_id:
        print(f"❌ No review ID for stage {stage_num}")
        return None
    
    review_file = reviews_dir / f"{review_id.replace('review:', 'review_')}.json"
    
    if not review_file.exists():
        print(f"❌ Review file not found: {review_file}")
        return None
    
    with open(review_file, 'r') as f:
        data = json.load(f)
    
    print(f"\n{'='*80}")
    print(f"STAGE {stage_num} - PEER REVIEW ANALYSIS")
    print(f"{'='*80}")
    print(f"Review ID: {review_id}")
    print(f"Status: {data.get('status')}")
    print(f"Final Verdict: {data.get('final_verdict')}")
    print(f"Critical Issues Count: {data.get('critical_issues_count', 0)}")
    print(f"Consensus: {data.get('consensus')}")
    print()
    
    # Extract issues from each reviewer
    print("CRITICAL ISSUES BY REVIEWER:")
    print("-" * 80)
    
    all_issues = []
    for reviewer in ['gemini_review', 'claude_review', 'chatgpt_review']:
        review = data.get(reviewer)
        if not review or not review.get('success'):
            print(f"\n{reviewer.replace('_review', '').upper()}: No review available")
            continue
        
        content = review.get('content', '')
        print(f"\n{reviewer.replace('_review', '').upper()} REVIEW:")
        print("-" * 40)
        
        # Print first 2000 chars of content
        preview = content[:2000]
        print(preview)
        if len(content) > 2000:
            print(f"\n... (truncated, {len(content)} total chars)")
        
        # Try to extract structured verdict
        if 'verdict' in review:
            print(f"\nVerdict: {review.get('verdict')}")
        if 'critical_issues' in review:
            print(f"Critical Issues: {len(review.get('critical_issues', []))}")
            for issue in review.get('critical_issues', [])[:5]:  # Show first 5
                print(f"  - {issue}")
    
    return data

def main():
    """Analyze all reviews."""
    print("="*80)
    print("PEER REVIEW ANALYSIS - STAGES 6-10")
    print("="*80)
    
    all_data = {}
    for stage_num in [6, 7, 8, 9, 10]:
        data = analyze_review(stage_num)
        if data:
            all_data[stage_num] = data
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for stage_num, data in all_data.items():
        print(f"Stage {stage_num}: {data.get('final_verdict')} ({data.get('critical_issues_count', 0)} issues)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
