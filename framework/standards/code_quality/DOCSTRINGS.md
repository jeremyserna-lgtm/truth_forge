# Docstrings

**All public functions MUST have docstrings using Google style.**

---

## Requirements

| Section | When Required |
|---------|---------------|
| Summary | Always (first line) |
| Args | When function has parameters |
| Returns | When function returns a value |
| Raises | When function raises exceptions |
| Example | Recommended for complex functions |

---

## Full Example

```python
def generate_entity_id(
    session_id: str,
    message_index: int,
    content: str,
) -> str:
    """Generate a deterministic entity ID for a message.

    Creates a stable, unique identifier based on session context and
    content hash. The ID is deterministic: same inputs always produce
    same output.

    Args:
        session_id: The session identifier (e.g., "abc123").
        message_index: Zero-based index of message within session.
        content: The message content to hash.

    Returns:
        A 32-character hexadecimal entity ID.

    Raises:
        ValueError: If session_id is empty or message_index is negative.

    Example:
        >>> generate_entity_id("sess_123", 0, "Hello world")
        'a1b2c3d4e5f6789012345678901234ab'
    """
    if not session_id:
        raise ValueError("session_id cannot be empty")
    if message_index < 0:
        raise ValueError("message_index cannot be negative")
    ...
```

---

## Anti-Pattern: Missing Docstrings

```python
# WRONG
def calculate_score(user_id, factors):
    weights = get_weights()
    return sum(f * w for f, w in zip(factors, weights))

# CORRECT
def calculate_score(user_id: str, factors: List[float]) -> float:
    """Calculate user engagement score from weighted factors.

    Args:
        user_id: The user identifier for logging.
        factors: List of factor values (0.0 to 1.0).

    Returns:
        Weighted sum of factors (0.0 to 100.0).
    """
    weights = get_weights()
    return sum(f * w for f, w in zip(factors, weights))
```

---

## When NOT to Write Docstrings

- **Private helpers** (`_internal_method`) - Optional
- **Self-evident functions** (`get_name() -> str`) - Optional but recommended
- **Test functions** - Test name should be descriptive enough

---

## UP

[code_quality/INDEX.md](INDEX.md)
