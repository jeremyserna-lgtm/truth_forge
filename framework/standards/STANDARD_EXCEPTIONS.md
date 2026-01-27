# Standard Exceptions

**Every standard must have a controlled path for exceptions.**

---

## The Rule

Exceptions must be documented, scoped narrowly, and tracked. Undocumented exceptions are technical debt.

---

## Exception Levels

| Level | Scope | Approval | Example |
|-------|-------|----------|---------|
| **1: Minor** | Single occurrence | Code reviewer | One function missing docstring |
| **2: Moderate** | Multiple occurrences | Standard owner | Module exempt during migration |
| **3: Major** | Project-wide | Standards Committee | Project exempt from standard |
| **4: Critical** | Organization-wide | Committee + Leadership | Security standard override |

---

## Override Format

```python
# standard:override [standard-name]-[requirement] - [justification]
```

| Component | Description | Example |
|-----------|-------------|---------|
| `standard:override` | Fixed prefix | `standard:override` |
| `standard-name` | Hyphenated name | `code-quality` |
| `requirement` | Hyphenated requirement | `type-hints-required` |
| `justification` | One-line reason | `Third-party library has no stubs` |

### Examples

```python
# CORRECT
# standard:override code-quality-type-hints - Third-party library has no stubs
result = untyped_lib.process(data)  # type: ignore

# CORRECT with expiration
# standard:override testing-coverage - Expires 2026-06-01, migration in progress
class LegacyModule:
    pass

# WRONG: No prefix (not searchable)
# Skipping type hints here
result = process(data)

# WRONG: No justification
# standard:override code-quality-type-hints
result = process(data)
```

---

## Documentation by Level

| Requirement | L1 | L2 | L3 | L4 |
|-------------|----|----|----|----|
| Inline comment | ✓ | ✓ | ✓ | ✓ |
| Justification | ✓ | ✓ | ✓ | ✓ |
| Tracking reference | - | ✓ | ✓ | ✓ |
| Expiration date | If temp | ✓ | ✓ | ✓ |
| ADR/RFC | - | - | ✓ | ✓ |
| Risk assessment | - | - | ✓ | ✓ |

---

## Scope Constraints

| Constraint | Rule |
|------------|------|
| **Narrow** | Exception scoped to smallest possible area |
| **Temporary** | Expiration date required for non-permanent exceptions |
| **Tracked** | Must be discoverable via `grep "standard:override"` |
| **Non-cascading** | Exception doesn't create exceptions in dependent code |

---

## Approval Authority

| Level | Authority | Timeline |
|-------|-----------|----------|
| Minor | Code reviewer | Immediate |
| Moderate | Standard owner | 48 hours |
| Major | Standards Committee | 1 week |
| Critical | Committee + Leadership | 2 weeks |

---

## Expiration and Review

| Type | Review Cycle |
|------|--------------|
| Temporary | Monthly until resolved |
| Permanent | Annually for continued need |
| Expired | Must be resolved or renewed |

---

## Industry Alignment

| System | Escape Mechanism |
|--------|------------------|
| Python mypy | `# type: ignore[error-code]` |
| ESLint | `// eslint-disable-next-line` |
| Ruff | `# noqa: CODE` |
| IETF RFCs | "SHOULD" vs "MUST" language |

---

## Framework Envelope

This standard is enveloped by:
- [06_LAW](../06_LAW.md) - Four Pillars (Fail-Safe principle)
- [00_GENESIS](../00_GENESIS.md) - THE GRAMMAR (naming conventions)

---

## UP

[INDEX.md](INDEX.md)
