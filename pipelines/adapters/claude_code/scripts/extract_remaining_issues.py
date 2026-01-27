#!/usr/bin/env python3
"""Extract remaining issues from peer reviews."""
import json
import sys
from pathlib import Path
from collections import defaultdict

reviews_dir = Path(__file__).parent.parent.parent.parent / "data" / "peer_reviews"

def extract_issues_from_review(content: str) -> list:
    """Extract critical issues from review content."""
    issues = []
    lines = content.split('\n')
    
    current_issue = None
    in_critical_section = False
    
    for line in lines:
        # Detect critical issue sections
        if any(marker in line for marker in ['CRITICAL ISSUE', 'Critical Issue', 'CRITICAL:', 'Critical:']):
            in_critical_section = True
            if current_issue:
                issues.append(current_issue.strip())
            current_issue = line
        elif in_critical_section:
            if line.strip() and (line.startswith('##') or line.startswith('**') and 'Issue' in line):
                if current_issue:
                    issues.append(current_issue.strip())
                current_issue = line
            elif current_issue:
                current_issue += ' ' + line
                if len(current_issue) > 500:  # Limit issue length
                    issues.append(current_issue.strip())
                    current_issue = None
    
    if current_issue:
        issues.append(current_issue.strip())
    
    return issues

def categorize_issue(issue_text: str) -> str:
    """Categorize an issue by type."""
    issue_lower = issue_text.lower()
    
    if 'sql injection' in issue_lower or 'sql' in issue_lower and 'injection' in issue_lower:
        return 'SQL Injection'
    elif 'memory' in issue_lower and ('exhaustion' in issue_lower or 'management' in issue_lower or 'load' in issue_lower):
        return 'Memory Management'
    elif 'turn' in issue_lower and ('boundary' in issue_lower or 'pairing' in issue_lower or 'logic' in issue_lower):
        return 'Turn Boundary Logic'
    elif 'error handling' in issue_lower or 'exception' in issue_lower:
        return 'Error Handling'
    elif 'verification' in issue_lower or 'verify' in issue_lower:
        return 'Verification Scripts'
    elif 'trust' in issue_lower or 'fidelity' in issue_lower or 'honesty' in issue_lower:
        return 'Trust Reports'
    elif 'security' in issue_lower or 'vulnerability' in issue_lower:
        return 'Security'
    elif 'scalability' in issue_lower or 'scale' in issue_lower:
        return 'Scalability'
    else:
        return 'Other'

def main():
    """Extract issues from all recent reviews."""
    review_files = sorted(reviews_dir.glob('review_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:17]
    
    all_issues_by_stage = defaultdict(lambda: defaultdict(list))
    all_issues_by_category = defaultdict(list)
    
    print("=" * 80)
    print("REMAINING ISSUES FROM PEER REVIEWS")
    print("=" * 80)
    print()
    
    for rf in review_files:
        with open(rf) as f:
            data = json.load(f)
        
        file_path = data.get('object_path', '')
        if 'stage_' in file_path and 'claude_code_stage' in file_path:
            stage_num = file_path.split('stage_')[1].split('/')[0]
            status = data.get('status', 'UNKNOWN')
            verdict = data.get('final_verdict', 'UNKNOWN')
            
            # Only analyze completed or partial reviews
            if status in ['COMPLETED', 'PARTIAL']:
                for reviewer_key in ['gemini_review', 'claude_review', 'chatgpt_review']:
                    review = data.get(reviewer_key, {})
                    if review.get('success'):
                        content = review.get('content', '')
                        issues = extract_issues_from_review(content)
                        
                        for issue in issues:
                            category = categorize_issue(issue)
                            all_issues_by_stage[stage_num][category].append({
                                'reviewer': reviewer_key.replace('_review', ''),
                                'issue': issue[:300]  # Truncate for readability
                            })
                            all_issues_by_category[category].append({
                                'stage': stage_num,
                                'reviewer': reviewer_key.replace('_review', ''),
                                'issue': issue[:300]
                            })
    
    # Print by stage
    print("ISSUES BY STAGE:")
    print("=" * 80)
    for stage in sorted(all_issues_by_stage.keys(), key=int):
        print(f"\nStage {stage}:")
        print("-" * 80)
        for category, issues in sorted(all_issues_by_stage[stage].items()):
            print(f"\n  {category} ({len(issues)} issues):")
            for issue_data in issues[:3]:  # Show first 3 per category
                print(f"    [{issue_data['reviewer']}] {issue_data['issue']}")
    
    # Print by category
    print("\n\n" + "=" * 80)
    print("ISSUES BY CATEGORY:")
    print("=" * 80)
    for category in sorted(all_issues_by_category.keys()):
        issues = all_issues_by_category[category]
        print(f"\n{category} ({len(issues)} total issues):")
        print("-" * 80)
        for issue_data in issues[:5]:  # Show first 5 per category
            print(f"  Stage {issue_data['stage']} [{issue_data['reviewer']}]: {issue_data['issue']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
