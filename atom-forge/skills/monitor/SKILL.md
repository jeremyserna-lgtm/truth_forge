# Monitor — Atomization Pipeline Status

## IDENTITY

You monitor the Atom-Forge pipeline: what's been processed, what's pending, deduplication rates, enrichment coverage, and cost tracking.

## MONITORING QUERIES

### Check Processing Status
```
What sessions have been processed?
→ Read processing_log.jsonl for completed sessions
→ Compare against sessions-index.json for total scope
→ Report: {processed}/{total} sessions ({percentage}%)
```

### Enrichment Coverage Report
```
How enriched are my atoms?
→ Query knowledge_atoms for enrichment_coverage distribution
→ Report:
  - Atoms at 100% coverage: {count}
  - Atoms at 50-99%: {count}
  - Atoms at 1-49%: {count}
  - Atoms at 0% (unenriched): {count}
  - Average coverage: {percentage}%
```

### Deduplication Report
```
How much deduplication is happening?
→ Read atomization reports
→ Report:
  - Total atoms extracted: {count}
  - Duplicates caught: {count} ({percentage}%)
    - Gate 1 (hash): {count}
    - Gate 2 (similarity): {count}
    - Gate 3 (graph): {count}
  - Net new atoms: {count}
  - Deduplication efficiency: {percentage}%
```

### Cost Report
```
How much has processing cost?
→ Sum token usage across all processed sessions
→ Report:
  - Sessions processed: {count}
  - Total input tokens: {count}
  - Total output tokens: {count}
  - Estimated cost: ${amount}
  - Budget remaining: ${remaining} of ${limit}
  - Cost per atom: ${amount}
```

### Source Coverage
```
Which sources are feeding atoms?
→ Query knowledge_atoms GROUP BY source_system
→ Report:
  - claude_code: {count} atoms from {sessions} sessions
  - gemini: {count} atoms
  - text_messages: {count} atoms
  - documents: {count} atoms
  - Total: {count} atoms across {sources} sources
```

## WHEN TO USE THIS SKILL

- User asks "how are we doing", "what's the status", "how much has been processed"
- User wants to know enrichment coverage or deduplication rates
- User asks about costs or budget
- User wants to see which sources are contributing atoms
- After a batch processing run, to review results
