---
description: "Generate new content based on your requirements"
argument-hint: "<what to create>"
---

# /create - Generate Content

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/create <description of what you need>
```

## Workflow

### 1. INPUT HOLD — Understand Requirements
Determine content type, audience, tone, length, and key points to cover.
If previous traces exist, read them to learn from past content creation decisions.

### 2. AGENT — Research and Draft
Gather relevant context from connected sources if needed.
Use the `creator-skill` skill to generate the content following appropriate patterns and templates.

### 3. OUTPUT HOLD — Review and Deliver
Self-check: Does it meet the requirements? Is the tone right? Any gaps?
Save the output as the appropriate file type (markdown, docx, html, etc.).

### 4. TRACE — Persist the AGENT Layer
Emit three files to the trace/ directory:
- WORK_create_[timestamp].md — the content produced and its specifications
- TRACE_create_[timestamp].md — tone decisions, structure choices, research consulted, confidence in accuracy
- FILTER_create_[timestamp].md — which approaches/angles were noise vs signal

## Examples
```
/create A blog post about the benefits of async communication for remote teams
/create An executive summary of Q4 performance for the board
```
