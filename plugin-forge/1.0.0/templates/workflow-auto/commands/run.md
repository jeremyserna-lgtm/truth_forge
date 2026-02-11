---
description: "Execute the automated workflow end-to-end"
argument-hint: "<trigger context or 'auto'>"
---

# /run - Execute Workflow

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/run <trigger context>
/run auto
```

## Workflow

### 1. INPUT HOLD — Gather and Validate Trigger Data
Check the trigger source for new events, inputs, or conditions that initiate the workflow.
Validate all required data is present and the workflow can proceed.
If previous traces exist, read FILTER.md to learn from past runs.

### 2. AGENT — Execute Steps
Use the `workflow-skill` skill to execute each step in sequence, handling errors and retries.

### 3. OUTPUT HOLD — Deliver Results
Send outputs to the action target and confirm completion.
Record the execution for status tracking and future reference.

### 4. TRACE — Persist the AGENT Layer
Emit three files to the trace/ directory:
- WORK_run_[timestamp].md — steps executed, results produced, status of each step
- TRACE_run_[timestamp].md — decisions at each branch point, why steps were ordered this way, errors encountered
- FILTER_run_[timestamp].md — which workflow paths were productive vs dead ends

## Examples
```
/run Check for new support tickets and create follow-up tasks
/run auto
```
