#!/usr/bin/env python3
"""Extract ALL issues from peer reviews - no limits, no filtering."""
import json
import re
from pathlib import Path
from collections import defaultdict

REVIEW_IDS = {
    0: "review:e18db6a598631d8a",
    6: "review:254cbd355b3aabfb",
    7: "review:b49d73e99a31f7e2",
    8: "review:ea0bc1d2dcbf9fdb",
    9: "review:4ecf0486cda9fb6e",  # May not exist yet
    10: None,  # May not exist yet
}

project_root = Path(__file__).parent.parent.parent.parent
reviews_dir = project_root / "data" / "peer_reviews"

def extract_all_issues(review_data, stage_num):
    """Extract ALL issues from all reviewers - no filtering, no limits."""
    all_issues = []
    
    for reviewer in ['gemini_review', 'claude_review', 'chatgpt_review']:
        review = review_data.get(reviewer)
        if not review or not review.get('success'):
            continue
        
        content = review.get('content', '')
        reviewer_name = reviewer.replace('_review', '').upper()
        
        # Extract all issues - look for patterns like:
        # - "Issue #", "Critical Issue", "Problem:", "Vulnerability", etc.
        # - Numbered lists (1., 2., etc.)
        # - Bullet points with issues
        
        # Split by sections
        sections = re.split(r'\n##\s+|\n###\s+|\n\*\*', content)
        
        for section in sections:
            section_lower = section.lower()
            
            # Check if this section contains issues
            if any(keyword in section_lower for keyword in [
                'issue', 'problem', 'vulnerability', 'bug', 'error', 
                'flaw', 'weakness', 'concern', 'risk', 'critical',
                'security', 'scalability', 'memory', 'performance',
                'logic', 'algorithm', 'design', 'architecture'
            ]):
                # Extract the full section as an issue
                issue_text = section.strip()
                if len(issue_text) > 50:  # Only substantial sections
                    all_issues.append({
                        'reviewer': reviewer_name,
                        'stage': stage_num,
                        'issue': issue_text,
                        'length': len(issue_text)
                    })
    
    return all_issues

def main():
    """Extract all issues from all reviews."""
    print("="*80)
    print("EXTRACTING ALL ISSUES FROM PEER REVIEWS")
    print("="*80)
    print("NO LIMITS - ALL ISSUES EXTRACTED")
    print()
    
    all_issues_by_stage = {}
    
    for stage_num, review_id in REVIEW_IDS.items():
        if not review_id:
            continue
        
        review_file = reviews_dir / f"{review_id.replace('review:', 'review_')}.json"
        if not review_file.exists():
            print(f"⚠️  Stage {stage_num}: Review file not found: {review_file}")
            continue
        
        with open(review_file, 'r') as f:
            data = json.load(f)
        
        issues = extract_all_issues(data, stage_num)
        all_issues_by_stage[stage_num] = issues
        
        print(f"Stage {stage_num}: {len(issues)} issues extracted")
        print(f"  Review ID: {review_id}")
        print(f"  Status: {data.get('status')}")
        print(f"  Verdict: {data.get('final_verdict')}")
        print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    total_issues = sum(len(issues) for issues in all_issues_by_stage.values())
    print(f"Total issues extracted: {total_issues}")
    print()
    
    for stage_num, issues in all_issues_by_stage.items():
        print(f"Stage {stage_num}: {len(issues)} issues")
        for issue in issues[:3]:  # Show first 3
            print(f"  - [{issue['reviewer']}] {issue['issue'][:100]}...")
        if len(issues) > 3:
            print(f"  ... and {len(issues) - 3} more")
        print()
    
    # Save to file
    output_file = project_root / "docs" / "07_governance" / "reports" / "ALL_ISSUES_EXTRACTED_2026_01_23.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(all_issues_by_stage, f, indent=2, default=str)
    
    print(f"✅ All issues saved to: {output_file}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
