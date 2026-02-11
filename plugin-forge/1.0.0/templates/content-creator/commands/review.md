---
description: "Review and improve existing content"
argument-hint: "<content or file to review>"
---

# /review - Review Content

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

## Usage
```
/review <paste content or reference a file>
```

## Workflow

### 1. INPUT HOLD — Receive and Analyze Content
Read the content and assess: clarity, accuracy, tone, structure, completeness.

### 2. AGENT — Identify Issues and Improve
Flag specific problems with actionable suggestions.
Use the `creator-skill` skill to offer a revised version addressing the issues found.

### 3. OUTPUT HOLD — Deliver Comparison
Show before/after with changes highlighted.

### 4. TRACE — Persist the AGENT Layer
Emit three files to the trace/ directory:
- WORK_review_[timestamp].md — the review feedback and suggested improvements
- TRACE_review_[timestamp].md — quality criteria applied, what stood out, confidence in suggestions
- FILTER_review_[timestamp].md — which review criteria were most relevant vs noise
