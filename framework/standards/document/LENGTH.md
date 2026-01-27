# LENGTH

**300 lines maximum. Reality-validated. Enforced always.**

---

## The Rule

Every document: **300 lines maximum.** No exceptions.

---

## Why This Limit

| Domain | Validation |
|--------|------------|
| **AI** | 300 lines (~5K tokens) well within context sweet spots |
| **Human** | Readable in one sitting (~10-15 minutes) |
| **Framework** | Forces proper anchoring, prevents sprawl |

---

## AI Context Research

| AI Model | Context Window | 300 Lines |
|----------|---------------|-----------|
| Claude 4 | 200K tokens | ~2.5% |
| GPT-5 | 400K tokens | ~1.25% |
| Llama 4 | 10M tokens | ~0.05% |

**"Lost in the Middle"** — Attention degrades in middle of long contexts.

---

## Token Estimation

```
300 lines ≈ 4,500-6,000 tokens ≈ 3,750-4,500 words
```

---

## When Exceeded

Two operations:

| Operation | Direction | When |
|-----------|-----------|------|
| **Compress** | Inward | Language can be denser |
| **Expand** | Outward | Content needs another anchor |

---

## Storage vs Reading

300 lines is the **storage** format, not the reading format.

```
STORAGE (atomic):     READING (composed):
┌───┐ ┌───┐ ┌───┐     ┌─────────────────┐
│ A │ │ B │ │ C │  →  │   A + B + C     │
└───┘ └───┘ └───┘     └─────────────────┘
```

AI enables dynamic composition:
- Store at atomic size (≤300)
- Compose to any size when reading
- Decompose when writing

For external audiences: the **narrative service** composes documents into expansive forms. Short isn't compromise—it's the point.

---

## The Split Pattern

```
BEFORE (400 lines, 2 topics):
┌─────────────────────────┐
│ Document: X and Y       │
└─────────────────────────┘

AFTER (2 documents):
┌─────────────────┐  ┌─────────────────┐
│ Document: X     │  │ Document: Y     │
└─────────────────┘  └─────────────────┘
```

---

## UP

[INDEX.md](INDEX.md)
