# Project Structure Layer

**What project structure primitives ARE.**

---

## Why This Layer Exists

Structure is navigation. Where things live determines how quickly you find them. This layer defines the craft of organizing repositories so anyone can find anything.

---

## What A Project Structure Primitive IS

A project structure primitive is a **single aspect of organization** that ensures consistent, discoverable file placement.

Project structure primitives are:
- **Convention-driven**: Same place in every project
- **Purpose-clear**: Location implies function
- **Discoverable**: New contributors find things without asking

Project structure primitives are NOT:
- Code architecture (that's how code relates)
- Folder naming (that's THE GRAMMAR)
- Documentation (that's content, not location)

---

## The Navigation Principle

A developer should find a file without grep. Project structure primitives ensure that knowing WHAT something is tells you WHERE it lives.

---

## How Primitives Relate

Project structure primitives form an organization system:

```
Top Level            │  Purpose-Specific
────────────────────────────────────
ROOT                 │  SRC (code)
(project entry)      │  TESTS (verification)
                     │  DOCS (explanation)
                     │  DATA (storage)
```

Top level defines the skeleton. Purpose-specific fills it.

---

## UP

[INDEX.md](INDEX.md)
