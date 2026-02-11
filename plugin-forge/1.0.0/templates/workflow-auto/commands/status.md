---
description: "Check workflow execution history and current status"
argument-hint: ""
---

# /status - Workflow Status

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/status
```

## Workflow

### 1. INPUT HOLD — Determine Reporting Scope
Understand what time period or run count to report on.

### 2. AGENT — Gather Execution Data
Read the workflow execution history.
Use the `workflow-skill` skill to summarize recent runs, success/failure rates, and pending actions.

### 3. OUTPUT HOLD — Present Actionable Dashboard
Show recent runs, success/failure rates, and any pending actions.
If there are failures or bottlenecks, suggest fixes.

### 4. TRACE — Persist the AGENT Layer
Emit three files to the trace/ directory:
- WORK_status_[timestamp].md — the status report produced
- TRACE_status_[timestamp].md — what metrics were checked, how trends were interpreted
- FILTER_status_[timestamp].md — which metrics were noise vs signal
