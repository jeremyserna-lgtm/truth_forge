# Git Layer

**What git primitives ARE.**

---

## Why This Layer Exists

Git is collective memory. History tells the story of how code evolved. This layer defines the craft of creating history that can be understood by future readers.

---

## What A Git Primitive IS

A git primitive is a **single aspect of version control practice** that makes history readable and meaningful.

Git primitives are:
- **History-focused**: Optimizes for future readers
- **Atomic**: One change, one commit, one message
- **Collaborative**: Works in team contexts

Git primitives are NOT:
- Backup strategies (git is not backup)
- Deployment tools (git is not CD)
- Code review (that's process)

---

## The History Principle

Every commit is a letter to the future. Git primitives define HOW to write letters that future readers can understand, search, and learn from.

---

## How Primitives Relate

Git primitives form a history system:

```
Commits              │  Collaboration
────────────────────────────────────
COMMITS              │  BRANCHING
(atomic changes)     │  (parallel work)
MESSAGES             │  HISTORY
(explanation)        │  (clean narrative)
```

Commits capture work. Collaboration scales it.

---

## UP

[INDEX.md](INDEX.md)
