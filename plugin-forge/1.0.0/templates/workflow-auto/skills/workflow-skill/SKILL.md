---
name: workflow-skill
description: >
  Orchestrate multi-step automated workflows with trigger detection, step execution,
  error handling, and result delivery. Use when the user wants to automate a process,
  chain actions together, handle conditional logic between steps, or build
  trigger-action pipelines. Includes retry patterns, validation checkpoints,
  and execution logging.
---

# Workflow Orchestration Skill

## Step Execution Pattern

For each step in the workflow:
1. Check preconditions
2. Execute the action
3. Validate the result
4. Handle errors (retry, skip, or abort)
5. Pass outputs to the next step

## Error Handling
- Transient failures: retry up to 3 times with backoff
- Data validation failures: flag and ask user
- Permission failures: report and suggest fix

## Execution Log
Record each run with: timestamp, steps completed, errors encountered, outputs produced.

## Trace Awareness
When previous TRACE.md or FILTER.md files exist for this workflow:
1. Read the Attention Log — know which steps succeeded/failed last time
2. Read the Confidence Map — know which steps are flaky or uncertain
3. Read the Surplus Value — know what workflow insights emerged
4. Read the Filter — skip known dead-end paths, prioritize productive ones

## References
- See `references/workflow-patterns.md` for common automation patterns
