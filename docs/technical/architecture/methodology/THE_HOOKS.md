# THE HOOKS

The six-phase enforcement flow. Every hook knows its phase.

---

## The Six Phases

```
PHASE 0: REGISTRY CHECK ─────────────────────────────────────────┐
├── Hash content                                                 │
├── Hash matches approved? → SKIP ALL (run free)                 │
├── >85% similar to existing? → BLOCK (use existing)             │
└── New content? → Continue to write                             │
                                                                 │
WRITE OCCURS ←───────────────────────────────────────────────────┘
         │
PHASE 1: RULES CHECK ────────────────────────────────────────────┐
├── Missing patterns? → Auto-add                                 │
├── Wrong patterns? → Auto-fix                                   │
└── Can't fix? → Phase 2                                         │
                                                                 │
PHASE 2: LLM FIX ────────────────────────────────────────────────┤
├── claude -p "Fix these violations"                             │
├── 3 attempts max                                               │
└── Still broken? → Phase 3                                      │
                                                                 │
PHASE 3: BLOCK ──────────────────────────────────────────────────┤
├── File blocked from commit                                     │
├── Developer reviews                                            │
├── Fix manually? → Phase 5                                      │
└── Claim false positive? → Phase 4                              │
                                                                 │
PHASE 4: FALSE POSITIVE REVIEW GATE ─────────────────────────────┤
├── --false-positive "violation_id"                              │
├── claude -p "Is this actually a false positive?"               │
├── APPROVED → Phase 5 (with review_id)                          │
└── REJECTED → Block stands                                      │
                                                                 │
PHASE 5: STAMP + REGISTER ───────────────────────────────────────┘
├── 5a: STAMP (markdown only)
│   ├── Issue document_id via generate_document_id()
│   ├── Write frontmatter to file
│   └── Register ID in identity.id_registry
├── 5b: REGISTER (all tracked files)
│   ├── Hash content (SHA256)
│   ├── Store in DuckDB registry
│   └── Compute + store 1024-dim embedding
└── Next time: hash match → Phase 0 instant pass
```

---

## Which Phase, Which Event

| Phase | Event | Purpose |
|-------|-------|---------|
| **0** | PreToolUse | Block duplicates before write |
| **1-3** | Pre-commit | Validate, repair, block |
| **4** | CLI `--false-positive` | Review gate |
| **5** | PostToolUse | Register after write |

---

## Phase 0: PreToolUse (Block Duplicates)

**When**: Before Write/Edit/MultiEdit
**Decision**: ALLOW or BLOCK

### Pattern

```python
#!/usr/bin/env python3
"""Phase 0: Registry check - block duplicates."""

import json
import os
import sys
from pathlib import Path

SKIP_DIRS = {"venv", ".venv", "__pycache__", ".git", "_deprecated"}
TRACKED = {".py", ".md", ".yaml", ".yml"}


def check() -> str:
    """Return 'ALLOW' or 'BLOCK:reason'."""
    try:
        inp = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
    except json.JSONDecodeError:
        return "ALLOW"

    filepath = inp.get("file_path") or inp.get("path")
    content = inp.get("content") or inp.get("file_text")

    if not filepath or not content:
        return "ALLOW"

    path = Path(filepath)
    if path.suffix.lower() not in TRACKED:
        return "ALLOW"
    if set(path.parts) & SKIP_DIRS:
        return "ALLOW"

    try:
        from your_registry import check_before_write
        allowed, message = check_before_write(filepath, content)
        return "ALLOW" if allowed else f"BLOCK:{message}"
    except Exception:
        return "ALLOW"  # Fail open


if __name__ == "__main__":
    sys.stdout.write(check())
```

### Shell Wrapper

```bash
#!/bin/bash
RESULT=$(python3 "$(dirname "$0")/phase_0_check.py" 2>/dev/null)
if [[ "$RESULT" == BLOCK:* ]]; then
    echo "${RESULT#BLOCK:}" >&2
    exit 1
fi
exit 0
```

### hooks.json

```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit|MultiEdit",
    "hooks": [{"type": "command", "command": "/path/to/phase_0_check.sh"}]
  }]
}
```

---

## Phase 1-3: Pre-commit (Validate, Repair, Block)

**When**: Before git commit
**Flow**: Check → Auto-fix → LLM repair (3x) → Block or Pass

### Pattern

```python
#!/usr/bin/env python3
"""Phases 1-3: Validate, repair, block."""

import subprocess
import sys
from pathlib import Path

REQUIRED = [
    (r"from architect_central_services import", "Missing central services"),
    (r"get_logger\(__name__\)", "Missing logger"),
]

FORBIDDEN = [
    (r"\bprint\s*\(", "Use logger instead of print()"),
]

MAX_REPAIR_ATTEMPTS = 3


def get_staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True,
    )
    return [Path(f) for f in result.stdout.strip().split("\n") if f.endswith(".py")]


def check_file(filepath: Path) -> list[dict]:
    """Phase 1: Check for violations."""
    import re
    content = filepath.read_text()
    violations = []

    for pattern, message in REQUIRED:
        if not re.search(pattern, content):
            violations.append({
                "id": f"missing:{pattern[:20]}:{filepath.name}",
                "message": message,
                "fixable": True,
            })

    for pattern, message in FORBIDDEN:
        if re.search(pattern, content):
            violations.append({
                "id": f"forbidden:{pattern[:20]}:{filepath.name}",
                "message": message,
                "fixable": True,
            })

    return violations


def attempt_llm_repair(filepath: Path, violations: list[dict]) -> bool:
    """Phase 2: LLM repair (3 attempts)."""
    for attempt in range(MAX_REPAIR_ATTEMPTS):
        prompt = f"""Fix these violations in {filepath}:

{chr(10).join(v['message'] for v in violations)}

Read the file and fix the issues. Do not add unnecessary changes."""

        try:
            subprocess.run(
                ["claude", "-p", prompt],
                timeout=60, capture_output=True,
            )
            # Re-check after repair
            new_violations = check_file(filepath)
            if not new_violations:
                return True
        except Exception:
            pass

    return False


def escalate_to_backlog(filepath: Path, violations: list[dict]):
    """Escalate unfixed violations to backlog."""
    import json
    from datetime import datetime
    from pathlib import Path as P

    backlog = P.home() / ".primitive_engine" / "backlog.jsonl"
    backlog.parent.mkdir(parents=True, exist_ok=True)

    with open(backlog, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "filepath": str(filepath),
            "violations": violations,
            "status": "open",
        }) + "\n")


def main() -> int:
    files = get_staged_files()
    blocked = []

    for filepath in files:
        if not filepath.exists():
            continue

        # Phase 1: Check
        violations = check_file(filepath)
        if not violations:
            continue

        # Phase 2: LLM repair
        if attempt_llm_repair(filepath, violations):
            continue

        # Phase 3: Block
        escalate_to_backlog(filepath, violations)
        blocked.append((filepath, violations))

    if blocked:
        print("BLOCKED FILES:", file=sys.stderr)
        for filepath, violations in blocked:
            print(f"  {filepath}:", file=sys.stderr)
            for v in violations:
                print(f"    - {v['message']}", file=sys.stderr)
        print(f"\nFix violations or use --false-positive <id>", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: enforcement
        name: Enforcement (Phases 1-3)
        entry: python bin/hooks/enforcement.py
        language: system
        pass_filenames: false
        stages: [pre-commit]
```

---

## Phase 4: False Positive Review Gate

**When**: Developer claims `--false-positive`
**Decision**: LLM reviews, APPROVED or REJECTED

### Pattern

```python
def review_false_positive(filepath: str, violation_id: str) -> tuple[bool, str, str]:
    """Phase 4: LLM reviews false positive claim.

    Returns: (approved, reason, review_id)
    """
    import subprocess
    import uuid
    from pathlib import Path

    content = Path(filepath).read_text()

    prompt = f"""File: {filepath}
Violation: {violation_id}
Developer claims this is a false positive.

Read the file and evaluate the claim.
Reply EXACTLY: APPROVED: <reason> or REJECTED: <reason>

File content:
{content[:8000]}
"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=60,
        )
        response = result.stdout.strip().split('\n')[-1]

        if response.startswith("APPROVED:"):
            reason = response[9:].strip()
            review_id = f"FP-{uuid.uuid4().hex[:8]}"
            log_fp_review(violation_id, filepath, "APPROVED", reason, review_id)
            return True, reason, review_id

        else:
            reason = response[9:].strip() if response.startswith("REJECTED:") else response
            log_fp_review(violation_id, filepath, "REJECTED", reason, None)
            return False, reason, None

    except Exception as e:
        return False, f"Review failed: {e}", None


def log_fp_review(violation_id, filepath, decision, reason, review_id):
    """Log for audit trail."""
    import json
    from datetime import datetime
    from pathlib import Path

    fp_log = Path.home() / ".primitive_engine" / "audit" / "false_positive_reviews.jsonl"
    fp_log.parent.mkdir(parents=True, exist_ok=True)

    with open(fp_log, "a") as f:
        f.write(json.dumps({
            "violation_id": violation_id,
            "filepath": filepath,
            "decision": decision,
            "reason": reason,
            "review_id": review_id or "",
            "reviewed_at": datetime.utcnow().isoformat() + "Z",
        }) + "\n")
```

### CLI Integration

```python
parser.add_argument(
    "--false-positive",
    action="append",
    metavar="VIOLATION_ID",
    help="Claim false positive for a violation ID",
)

# In main():
if args.false_positive:
    for violation_id in args.false_positive:
        approved, reason, review_id = review_false_positive(filepath, violation_id)
        if approved:
            print(f"APPROVED: {reason} (review_id: {review_id})")
            # Continue to Phase 5 with review_id
        else:
            print(f"REJECTED: {reason}")
            sys.exit(1)
```

---

## Phase 5: PostToolUse (Register)

**When**: After Write/Edit/MultiEdit succeeds
**Purpose**: Register for future duplicate detection

### Pattern

```python
#!/usr/bin/env python3
"""Phase 5: Register approved documents."""

import json
import os
import sys
from pathlib import Path

SKIP_DIRS = {"venv", ".venv", "__pycache__", ".git", "_deprecated"}
TRACKED = {".py", ".md", ".yaml", ".yml"}


def register():
    try:
        inp = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
    except json.JSONDecodeError:
        return

    # Check tool succeeded
    try:
        result = json.loads(os.environ.get("CLAUDE_TOOL_RESULT", "{}"))
        if isinstance(result, dict) and result.get("error"):
            return
    except (json.JSONDecodeError, TypeError):
        pass

    filepath = inp.get("file_path") or inp.get("path")
    if not filepath:
        return

    path = Path(filepath)
    if path.suffix.lower() not in TRACKED:
        return
    if set(path.parts) & SKIP_DIRS:
        return
    if not path.exists():
        return

    try:
        content = path.read_text()
        from your_registry import register_approved
        from your_identity import generate_document_id

        doc_id = generate_document_id(str(path))
        register_approved(str(path), doc_id, content)
    except Exception:
        pass  # Best effort


if __name__ == "__main__":
    register()
```

### Shell Wrapper

```bash
#!/bin/bash
python3 "$(dirname "$0")/phase_5_register.py" 2>&1 >&2
exit 0  # Always succeed
```

### hooks.json

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit|MultiEdit",
    "hooks": [{"type": "command", "command": "/path/to/phase_5_register.sh"}]
  }]
}
```

---

## Duplication Check (Phase 0)

Two-tier detection:

```python
def check_duplication(content: str, filepath: str) -> tuple[bool, str]:
    """
    Returns (allowed, message).

    Tier 1: Hash check (fast, always works)
    Tier 2: Semantic similarity (if embeddings available)
    """
    # Tier 1: Hash
    content_hash = hash_content(content)
    existing = lookup_by_hash(content_hash)

    if existing:
        if existing.filepath == filepath:
            return True, "Same file (approved)"
        else:
            return False, f"Exact duplicate of {existing.filepath}"

    # Tier 2: Similarity
    if embeddings_available():
        embedding = embed_local(content[:8000])  # 1024-dim ONLY
        similar = find_similar(embedding, threshold=0.85)
        if similar:
            return False, f"Too similar ({similar.score:.0%}) to {similar.filepath}"

    return True, "New content"
```

---

## Correctness Check (Phases 1-3)

```python
import re

REQUIRED = [
    (r"from architect_central_services import", "Missing central services"),
    (r"get_logger\(__name__\)", "Missing logger setup"),
]

FORBIDDEN = [
    (r"\bprint\s*\(", "Use logger not print()"),
    (r"from google\.cloud import bigquery", "Use get_bigquery_client()"),
]


def check_correctness(content: str) -> list[str]:
    violations = []

    for pattern, message in REQUIRED:
        if not re.search(pattern, content):
            violations.append(message)

    for pattern, message in FORBIDDEN:
        if re.search(pattern, content):
            violations.append(message)

    return violations
```

---

## Summary Table

| Phase | Event | Input | Output | On Failure |
|-------|-------|-------|--------|------------|
| 0 | PreToolUse | `CLAUDE_TOOL_INPUT` | ALLOW/BLOCK | Fail open |
| 1-3 | Pre-commit | `git diff --cached` | Exit 0/1 | Repair 3x, then block |
| 4 | CLI | `--false-positive ID` | APPROVED/REJECTED | Block stands |
| 5 | PostToolUse | `CLAUDE_TOOL_INPUT` | (none) | Best effort |

---

## Storage

```
~/.primitive_engine/
├── registry/
│   ├── document_registry.duckdb  # Hash index, records
│   └── embeddings.npz            # 1024-dim vectors
├── backlog.jsonl                 # Unfixed violations (escalated)
└── audit/
    └── false_positive_reviews.jsonl
```

---

## The Principle

```
First approval is thorough. After that, scripts run free.
```

- New script? → Full 6-phase enforcement
- Approved script? → Hash match → Phase 0 instant pass
- False positive? → LLM review gate (not a bypass)
- Unfixed? → Escalate to backlog
