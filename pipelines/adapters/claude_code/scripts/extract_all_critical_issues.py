#!/usr/bin/env python3
"""Extract and analyze all critical issues from peer reviews."""
import json
from pathlib import Path
import re
from collections import defaultdict
from datetime import datetime

reviews_dir = Path('data/peer_reviews')
all_reviews = list(reviews_dir.glob('review_*.json'))

# Get reviews from last hour
cutoff_time = datetime.now().timestamp() - 3600
recent_reviews = [r for r in all_reviews if r.stat().st_mtime > cutoff_time]

all_issues = []
stage_issues = defaultdict(list)

for review_file in recent_reviews:
    try:
        with open(review_file, 'r') as f:
            data = json.load(f)
            
        object_path = data.get('object_path', '')
        stage_match = re.search(r'stage_(\d+)', object_path)
        if not stage_match:
            continue
        stage_num = int(stage_match.group(1))
        
        review_id = data.get('review_id', review_file.stem)
        
        # Get aggregated critical issues
        aggregated_issues = data.get('aggregated_critical_issues', [])
        if isinstance(aggregated_issues, list):
            for issue in aggregated_issues:
                issue_data = {
                    'stage': stage_num,
                    'review_id': review_id,
                    'issue': issue,
                    'source': 'aggregated'
                }
                all_issues.append(issue_data)
                stage_issues[stage_num].append(issue_data)
        
        # Also extract from individual reviewer responses
        for reviewer in ['gemini_review', 'claude_review', 'chatgpt_review']:
            review = data.get(reviewer, {})
            if not review or not review.get('success'):
                continue
            
            content = review.get('content', '')
            reviewer_name = reviewer.replace('_review', '')
            
            # Try to extract critical issues from content
            # Look for patterns like "Critical Issue:", "CRITICAL:", etc.
            lines = content.split('\n')
            current_issue = None
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Check if this is a critical issue marker
                if any(marker in line_lower for marker in [
                    'critical issue', 'critical:', 'severe issue', 
                    'major issue', 'security vulnerability', 'sql injection',
                    'memory leak', 'out of memory', 'scalability', 'logic error'
                ]):
                    if current_issue:
                        issue_data = {
                            'stage': stage_num,
                            'review_id': review_id,
                            'issue': current_issue.strip(),
                            'source': reviewer_name,
                            'line_context': lines[max(0, i-2):min(len(lines), i+5)]
                        }
                        all_issues.append(issue_data)
                        stage_issues[stage_num].append(issue_data)
                    
                    current_issue = line
                elif current_issue:
                    # Continue building the issue
                    if line.strip() and not line.strip().startswith('#'):
                        current_issue += ' ' + line
                    elif len(current_issue) > 500:  # Limit issue length
                        issue_data = {
                            'stage': stage_num,
                            'review_id': review_id,
                            'issue': current_issue.strip(),
                            'source': reviewer_name
                        }
                        all_issues.append(issue_data)
                        stage_issues[stage_num].append(issue_data)
                        current_issue = None
            
            if current_issue:
                issue_data = {
                    'stage': stage_num,
                    'review_id': review_id,
                    'issue': current_issue.strip(),
                    'source': reviewer_name
                }
                all_issues.append(issue_data)
                stage_issues[stage_num].append(issue_data)
    
    except Exception as e:
        print(f"Error processing {review_file}: {e}", file=sys.stderr)
        continue

# Categorize issues
categories = {
    'SQL Injection': [],
    'Memory/Scalability': [],
    'Logic Error': [],
    'Error Handling': [],
    'Security': [],
    'Data Validation': [],
    'Performance': [],
    'Code Quality': [],
    'Documentation': [],
    'Other': []
}

for issue_data in all_issues:
    issue_text = issue_data['issue'].lower() if isinstance(issue_data['issue'], str) else str(issue_data['issue']).lower()
    
    categorized = False
    if 'sql injection' in issue_text or 'sql injection' in issue_text:
        categories['SQL Injection'].append(issue_data)
        categorized = True
    elif 'memory' in issue_text or 'scalability' in issue_text or 'oom' in issue_text or 'out of memory' in issue_text or 'load all' in issue_text:
        categories['Memory/Scalability'].append(issue_data)
        categorized = True
    elif 'logic error' in issue_text or 'logic flaw' in issue_text or 'incorrect logic' in issue_text or 'wrong logic' in issue_text:
        categories['Logic Error'].append(issue_data)
        categorized = True
    elif 'error handling' in issue_text or 'exception' in issue_text or 'try/except' in issue_text or 'error handling' in issue_text:
        categories['Error Handling'].append(issue_data)
        categorized = True
    elif 'security' in issue_text or 'vulnerability' in issue_text or 'injection' in issue_text:
        categories['Security'].append(issue_data)
        categorized = True
    elif 'validation' in issue_text or 'validate' in issue_text or 'invalid' in issue_text:
        categories['Data Validation'].append(issue_data)
        categorized = True
    elif 'performance' in issue_text or 'slow' in issue_text or 'inefficient' in issue_text:
        categories['Performance'].append(issue_data)
        categorized = True
    elif 'documentation' in issue_text or 'docstring' in issue_text or 'comment' in issue_text:
        categories['Documentation'].append(issue_data)
        categorized = True
    elif 'code quality' in issue_text or 'refactor' in issue_text or 'cleanup' in issue_text:
        categories['Code Quality'].append(issue_data)
        categorized = True
    
    if not categorized:
        categories['Other'].append(issue_data)

# Generate report
print("=" * 120)
print("CRITICAL ISSUES ANALYSIS - ALL STAGES")
print("=" * 120)
print(f"Total Issues Extracted: {len(all_issues)}")
print(f"Stages with Issues: {len(stage_issues)}")
print()

print("ISSUES BY CATEGORY:")
print("-" * 120)
for category, issues in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
    if issues:
        print(f"{category}: {len(issues)} issues")
print()

print("ISSUES BY STAGE:")
print("-" * 120)
for stage_num in sorted(stage_issues.keys()):
    print(f"Stage {stage_num}: {len(stage_issues[stage_num])} issues")
print()

# Save detailed report
output_file = Path('pipelines/claude_code/scripts/ALL_CRITICAL_ISSUES_ANALYSIS.md')
with open(output_file, 'w') as f:
    f.write("# All Critical Issues Analysis\n\n")
    f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Total Issues**: {len(all_issues)}\n")
    f.write(f"**Stages Analyzed**: {len(stage_issues)}\n\n")
    
    f.write("## Issues by Category\n\n")
    for category, issues in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        if issues:
            f.write(f"### {category} ({len(issues)} issues)\n\n")
            for i, issue_data in enumerate(issues[:20], 1):  # Limit to first 20 per category
                f.write(f"{i}. **Stage {issue_data['stage']}** ({issue_data['source']}):\n")
                issue_text = issue_data['issue']
                if isinstance(issue_text, str):
                    # Truncate if too long
                    if len(issue_text) > 500:
                        issue_text = issue_text[:500] + "..."
                    f.write(f"   {issue_text}\n\n")
            if len(issues) > 20:
                f.write(f"   ... and {len(issues) - 20} more issues in this category\n\n")
    
    f.write("\n## Issues by Stage\n\n")
    for stage_num in sorted(stage_issues.keys()):
        issues = stage_issues[stage_num]
        f.write(f"### Stage {stage_num} ({len(issues)} issues)\n\n")
        for i, issue_data in enumerate(issues[:15], 1):  # Limit to first 15 per stage
            f.write(f"{i}. **{issue_data['source']}**:\n")
            issue_text = issue_data['issue']
            if isinstance(issue_text, str):
                if len(issue_text) > 300:
                    issue_text = issue_text[:300] + "..."
                f.write(f"   {issue_text}\n\n")
        if len(issues) > 15:
            f.write(f"   ... and {len(issues) - 15} more issues\n\n")

print(f"\n✅ Detailed analysis saved to: {output_file}")
