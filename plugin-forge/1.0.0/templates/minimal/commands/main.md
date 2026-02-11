---
description: "__COMMAND_DESCRIPTION__"
argument-hint: "<input>"
---

# /main - __PLUGIN_NAME__

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/main <input>
```

## Workflow

### 1. INPUT HOLD — Receive and validate
Parse the user's input and determine what they need.
If previous traces exist in `trace/`, read them to improve this operation.

### 2. AGENT — Transform through skill knowledge
Use the `example-skill` skill to process the request.

### 3. OUTPUT HOLD — Deliver surplus value
Present results clearly with relevant context.

### 4. TRACE — Persist the AGENT layer
Emit three files to the trace/ directory:
- WORK_main_[timestamp].md — summary of what was produced
- TRACE_main_[timestamp].md — decisions made, what was read/skipped, confidence levels, surprises
- FILTER_main_[timestamp].md — what was noise (drowning) vs signal (swimming) vs emerged (surplus)

## Examples
```
/main example input here
```
