#!/usr/bin/env python3
"""Extract structured critical issues from peer reviews."""
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
        
        # PRIMARY: Get aggregated critical issues (official list)
        aggregated_issues = data.get('aggregated_critical_issues', [])
        if isinstance(aggregated_issues, list):
            for issue in aggregated_issues:
                if issue and isinstance(issue, str) and len(issue.strip()) > 10:
                    issue_data = {
                        'stage': stage_num,
                        'review_id': review_id,
                        'issue': issue.strip(),
                        'source': 'aggregated',
                        'priority': 'HIGH'  # Aggregated issues are high priority
                    }
                    all_issues.append(issue_data)
                    stage_issues[stage_num].append(issue_data)
        
        # SECONDARY: Extract structured issues from reviewer content
        for reviewer in ['gemini_review', 'claude_review', 'chatgpt_review']:
            review = data.get(reviewer, {})
            if not review or not review.get('success'):
                continue
            
            content = review.get('content', '')
            reviewer_name = reviewer.replace('_review', '')
            
            # Look for structured issue patterns
            # Pattern 1: "CRITICAL ISSUE #X:" or "Critical Issue #X:"
            critical_pattern = re.compile(
                r'(?:CRITICAL\s+)?ISSUE\s+#?\d+[:\-]?\s*(.+?)(?=\n(?:CRITICAL\s+)?ISSUE\s+#?\d+[:\-]?|$)',
                re.IGNORECASE | re.DOTALL
            )
            
            for match in critical_pattern.finditer(content):
                issue_text = match.group(1).strip()
                # Clean up the issue text
                issue_text = re.sub(r'\s+', ' ', issue_text)
                if len(issue_text) > 50:  # Only keep substantial issues
                    issue_data = {
                        'stage': stage_num,
                        'review_id': review_id,
                        'issue': issue_text[:500],  # Limit length
                        'source': reviewer_name,
                        'priority': 'MEDIUM'
                    }
                    all_issues.append(issue_data)
                    stage_issues[stage_num].append(issue_data)
            
            # Pattern 2: "### CRITICAL ISSUE" or "## CRITICAL ISSUE"
            critical_header_pattern = re.compile(
                r'#{1,3}\s+CRITICAL\s+ISSUE[:\-]?\s*(.+?)(?=\n#{1,3}\s+(?:CRITICAL\s+)?ISSUE|$)',
                re.IGNORECASE | re.DOTALL
            )
            
            for match in critical_header_pattern.finditer(content):
                issue_text = match.group(1).strip()
                issue_text = re.sub(r'\s+', ' ', issue_text)
                if len(issue_text) > 50:
                    issue_data = {
                        'stage': stage_num,
                        'review_id': review_id,
                        'issue': issue_text[:500],
                        'source': reviewer_name,
                        'priority': 'HIGH'
                    }
                    all_issues.append(issue_data)
                    stage_issues[stage_num].append(issue_data)
    
    except Exception as e:
        print(f"Error processing {review_file}: {e}", file=__import__('sys').stderr)
        continue

# Categorize issues
categories = {
    'SQL Injection': [],
    'Memory/Scalability': [],
    'Logic Error': [],
    'Error Handling': [],
    'Security': [],
    'Data Validation': [],
    'Non-Coder Accessibility': [],
    'Documentation': [],
    'Performance': [],
    'Code Quality': [],
    'Other': []
}

for issue_data in all_issues:
    issue_text = issue_data['issue'].lower()
    
    categorized = False
    if 'sql injection' in issue_text:
        categories['SQL Injection'].append(issue_data)
        categorized = True
    elif 'memory' in issue_text or 'scalability' in issue_text or 'oom' in issue_text or 'out of memory' in issue_text or 'load all' in issue_text or 'memory exhaustion' in issue_text:
        categories['Memory/Scalability'].append(issue_data)
        categorized = True
    elif 'logic error' in issue_text or 'logic flaw' in issue_text or 'incorrect logic' in issue_text or 'wrong logic' in issue_text or 'logic bug' in issue_text:
        categories['Logic Error'].append(issue_data)
        categorized = True
    elif 'error handling' in issue_text or 'exception' in issue_text or 'try/except' in issue_text or 'error handling' in issue_text or 'silent failure' in issue_text:
        categories['Error Handling'].append(issue_data)
        categorized = True
    elif 'non-coder' in issue_text or 'non coding' in issue_text or 'non-coding' in issue_text or 'non coder' in issue_text or 'user-friendly' in issue_text or 'non-technical' in issue_text:
        categories['Non-Coder Accessibility'].append(issue_data)
        categorized = True
    elif 'security' in issue_text or 'vulnerability' in issue_text or 'injection' in issue_text or 'path traversal' in issue_text:
        categories['Security'].append(issue_data)
        categorized = True
    elif 'validation' in issue_text or 'validate' in issue_text or 'invalid' in issue_text or 'schema' in issue_text:
        categories['Data Validation'].append(issue_data)
        categorized = True
    elif 'performance' in issue_text or 'slow' in issue_text or 'inefficient' in issue_text or 'bottleneck' in issue_text:
        categories['Performance'].append(issue_data)
        categorized = True
    elif 'documentation' in issue_text or 'docstring' in issue_text or 'comment' in issue_text or 'trust report' in issue_text or 'fidelity report' in issue_text:
        categories['Documentation'].append(issue_data)
        categorized = True
    elif 'code quality' in issue_text or 'refactor' in issue_text or 'cleanup' in issue_text or 'duplicate' in issue_text:
        categories['Code Quality'].append(issue_data)
        categorized = True
    
    if not categorized:
        categories['Other'].append(issue_data)

# Generate prioritized report
output_file = Path('pipelines/claude_code/scripts/CRITICAL_ISSUES_PRIORITIZED.md')
with open(output_file, 'w') as f:
    f.write("# Critical Issues Analysis - Prioritized\n\n")
    f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Total Issues**: {len(all_issues)}\n")
    f.write(f"**Stages Analyzed**: {len(stage_issues)}\n\n")
    
    # Priority order: Security > Memory/Scalability > Logic Error > Error Handling > Non-Coder > Others
    priority_order = [
        'SQL Injection',
        'Security',
        'Memory/Scalability',
        'Logic Error',
        'Error Handling',
        'Data Validation',
        'Non-Coder Accessibility',
        'Performance',
        'Code Quality',
        'Documentation',
        'Other'
    ]
    
    f.write("## Executive Summary\n\n")
    f.write("### Issues by Category (Priority Order)\n\n")
    for category in priority_order:
        issues = categories[category]
        if issues:
            f.write(f"- **{category}**: {len(issues)} issues\n")
    
    f.write("\n### Issues by Stage\n\n")
    for stage_num in sorted(stage_issues.keys()):
        f.write(f"- **Stage {stage_num}**: {len(stage_issues[stage_num])} issues\n")
    
    f.write("\n---\n\n")
    f.write("## Detailed Issues by Category\n\n")
    
    for category in priority_order:
        issues = categories[category]
        if not issues:
            continue
        
        f.write(f"### {category} ({len(issues)} issues)\n\n")
        
        # Sort by priority (HIGH first) then by stage
        sorted_issues = sorted(issues, key=lambda x: (x.get('priority', 'LOW') != 'HIGH', x['stage']))
        
        for i, issue_data in enumerate(sorted_issues[:50], 1):  # Limit to top 50 per category
            f.write(f"{i}. **Stage {issue_data['stage']}** ({issue_data['source']}, {issue_data.get('priority', 'MEDIUM')}):\n")
            issue_text = issue_data['issue']
            if isinstance(issue_text, str):
                # Clean up and format
                issue_text = issue_text.replace('\n', ' ').strip()
                if len(issue_text) > 400:
                    issue_text = issue_text[:400] + "..."
                f.write(f"   {issue_text}\n\n")
        
        if len(issues) > 50:
            f.write(f"   *... and {len(issues) - 50} more issues in this category*\n\n")
    
    f.write("\n---\n\n")
    f.write("## Issues by Stage\n\n")
    
    for stage_num in sorted(stage_issues.keys()):
        issues = stage_issues[stage_num]
        f.write(f"### Stage {stage_num} ({len(issues)} issues)\n\n")
        
        # Sort by priority
        sorted_issues = sorted(issues, key=lambda x: (x.get('priority', 'LOW') != 'HIGH', x['source']))
        
        for i, issue_data in enumerate(sorted_issues[:30], 1):  # Limit to top 30 per stage
            f.write(f"{i}. **{issue_data['source']}** ({issue_data.get('priority', 'MEDIUM')}):\n")
            issue_text = issue_data['issue']
            if isinstance(issue_text, str):
                issue_text = issue_text.replace('\n', ' ').strip()
                if len(issue_text) > 300:
                    issue_text = issue_text[:300] + "..."
                f.write(f"   {issue_text}\n\n")
        
        if len(issues) > 30:
            f.write(f"   *... and {len(issues) - 30} more issues*\n\n")

print("=" * 120)
print("CRITICAL ISSUES ANALYSIS - STRUCTURED EXTRACTION")
print("=" * 120)
print(f"Total Issues Extracted: {len(all_issues)}")
print(f"Stages with Issues: {len(stage_issues)}")
print()

print("ISSUES BY CATEGORY (Priority Order):")
print("-" * 120)
priority_order = [
    'SQL Injection', 'Security', 'Memory/Scalability', 'Logic Error',
    'Error Handling', 'Data Validation', 'Non-Coder Accessibility',
    'Performance', 'Code Quality', 'Documentation', 'Other'
]
for category in priority_order:
    issues = categories[category]
    if issues:
        print(f"{category}: {len(issues)} issues")

print()
print(f"✅ Detailed analysis saved to: {output_file}")
