---
description: "Query your data source with natural language"
argument-hint: "<question about your data>"
---

# /query - Query Data Source

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/query <natural language question>
```

## Workflow

### 1. INPUT HOLD — Parse the Question
Determine what data is needed, which tables/collections, and what filters apply.
If previous traces exist in `trace/`, read FILTER.md to skip known noise.

### 2. AGENT — Build and Execute Query
Use the `connector-skill` skill to write the appropriate query for your data source dialect.

### 3. OUTPUT HOLD — Validate and Present Results
Check for unexpected nulls, row counts that make sense, and reasonable value ranges.
Lead with the answer, then show supporting data.

### 4. TRACE — Persist the AGENT Layer
Emit three files to the trace/ directory:
- WORK_query_[timestamp].md — the query executed and results returned
- TRACE_query_[timestamp].md — how the query was constructed, what schema paths were considered, confidence in interpretation
- FILTER_query_[timestamp].md — what query approaches were noise vs signal

## Examples
```
/query How many new records were created last week?
/query What are the top 10 entries by value?
```
