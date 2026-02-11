# No Magic Numbers

**Parent:** Technical Architecture → Zero Trust Standard
**Mind Map Path:** NOT-ME Sovereign AI Ecosystem → Technical Architecture → Zero Trust Standard → No magic numbers

---

## Definition

**"No Magic Numbers"** is a foundational technical mandate within the Zero Trust Standard. A "Magic Number" is any hardcoded integer (e.g., `max_tokens=2048`, `limit=10`, `batch_size=5`) buried in the code that acts as an invisible boundary for the AI's operations.

### The Core Rule

- **The Rule:** The "Magic Number Count" in the codebase must be **0**.
- **The Requirement:** Every numeric limit must be defined as a **named constant** that traces back to a visible `HUMAN_DECISION` or a logged `AI_DEFAULT`.
- **The Goal:** Prevent the AI from making arbitrary choices about resource allocation or attention that the user cannot see.

### The Problem: "Invisible Decisions"

Standard AI agents are plagued by "Invisible Decisions." Engineers often hardcode limits to save costs or latency (e.g., "only read the first 5 search results"), but the user assumes the AI read everything.

- **Silent Truncation:** Sibling issue to magic numbers. If an AI silently cuts text to fit context window, it is "lying by omission."
- **The Threat:** For a non-technical user, hidden numbers create a "false done" state, where the user trusts a comprehensive result that was actually arbitrarily limited.

## Boundaries

### What No Magic Numbers IS:
- Zero hardcoded integers acting as invisible boundaries
- All limits traced to HUMAN_DECISION or logged AI_DEFAULT
- Named constants replacing inline numbers
- Architectural enforcement of transparency

### What No Magic Numbers IS NOT:
- Suggestion for good coding style (it's mandatory)
- Allowing hidden limits for performance
- Silent filtering for efficiency
- Any numeric limit without decision source logging

## Relationship to Other Nodes

| Related Node | Relationship |
|--------------|--------------|
| No silent truncation | Sibling constraint |
| Decision transparency | Sibling constraint |
| Zero Trust Standard | Parent principle |
| config.json | Implementation location |

## Implementation Constraints

### Architectural Enforcement

- **The Linter:** `zero_trust_linter.py` scans code contributions. If it detects hardcoded limits without decision sourcing, it rejects the build.
- **The Metadata Layer (`_meta`):** Every response must include a `_meta` block displaying specific limits and architectural constraints applied.
- **Decision Source Logging:** Every limit must log its `decision_source`. The system must answer: "Did Jeremy set this limit, or did the AI default to it?"

### Hardware Dependency

The enforcement of "No Magic Numbers" is directly linked to **Sovereign Exocompute** (local hardware).

- **Cloud Opacity:** Public cloud models rely on invisible optimization techniques. You cannot enforce "No Magic Numbers" on a system you do not own.
- **Local Control:** By running locally, the user controls the entire stack, ensuring no API gateway silently filters based on arbitrary magic numbers.

## Verification

1. **Count Test:** Is the Magic Number Count exactly 0?
2. **Traceability Test:** Does every limit trace to HUMAN_DECISION or AI_DEFAULT?
3. **Named Constant Test:** Are all limits defined as named constants?
4. **Linter Test:** Does the codebase pass `zero_trust_linter.py`?

---

*Source: NotebookLM synthesis from corpus*
*Status: COMPLETE*
