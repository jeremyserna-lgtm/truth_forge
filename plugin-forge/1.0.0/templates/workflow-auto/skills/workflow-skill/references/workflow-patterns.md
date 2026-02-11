# Workflow Patterns

## Sequential Pipeline
Step A → Step B → Step C. Each step depends on the previous.

## Fan-Out
Step A → (Step B1, Step B2, Step B3) → Collect → Step C.
Process multiple items in parallel, then aggregate.

## Conditional Branch
Step A → IF condition THEN Step B ELSE Step C → Step D.

## Retry Loop
Step A → IF failure AND retries < 3 THEN Step A ELSE escalate.

## Approval Gate
Step A → Wait for user approval → Step B.
