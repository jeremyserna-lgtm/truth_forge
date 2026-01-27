# LAYER

**Each document belongs to exactly ONE layer.**

---

## The Rule

Content stays in its layer. Wrong-layer content must be moved.

---

## The Layers

| Layer | Contains | Does NOT Contain |
|-------|----------|------------------|
| **Theory** | Principles, philosophy | Code, implementation |
| **Meta** | Rules about rules | Specific implementations |
| **Specifics** | Technical requirements | Philosophy |
| **Primitives** | Atomic rules | Abstract principles |

---

## Layer Locations

| Layer | Location |
|-------|----------|
| Theory | `framework/*.md` |
| Meta | `standards/STANDARD_*.md` |
| Specifics | `standards/{name}/INDEX.md` |
| Primitives | `standards/{name}/*.md` |

---

## Determining Layer

| Question | Layer |
|----------|-------|
| Is this a principle or pattern? | Theory |
| Is this a rule about standards? | Meta |
| Is this a specific requirement? | Specifics |
| Is this an atomic, irreducible rule? | Primitives |

---

## The Bleed Test

If you see:
- Code in theory → Move to primitives
- Philosophy in specifics → Move to theory
- Implementation in meta → Move to specifics

---

## UP

[INDEX.md](INDEX.md)
