# Document Primitives

## Two Document Types

```
Technology Documents          Human-Facing Documents
(transport within substrate)  (membrane to Jeremy)
        │                            ▲
        ▼                            │
   RAG System ──► Knowledge Atoms ───┘
   Context Window    (extraction)   (synthesis)
```

| Type | Purpose | Optimized For | Who Reads It |
|------|---------|---------------|--------------|
| **Technology Document** | Transport within substrate | Machine processing | Claude, RAG, Knowledge Atom system |
| **Human-Facing Document** | Translation layer | Human cognition | Jeremy |

**This document describes Technology Documents.**

Human-Facing Documents are a separate primitive with different constraints (human cognition, not machine limits). They are synthesized FROM knowledge atoms, not written directly.

---

## The Chain (Technology Documents)

```
Plan (do-now) → Document (exist-now) → Context Window (substrate)
                                    → RAG System (chunking)
                                    → Knowledge Atoms (extraction)
```

A plan produces a document. A technology document is processed by Claude, chunked by RAG, decomposed into knowledge atoms.

If the document exceeds what these systems can handle, the document fails its purpose.

## The Physical Constraint

The context window is finite (~200K tokens). It is shared:
- CLAUDE.md and rules (already loaded)
- Conversation history (grows during work)
- Tool outputs (unpredictable)
- Documents read for the work

A document's budget is not the full context window. It competes for space.

### Size Limits

| Lines | Tokens | Context Share | Assessment |
|-------|--------|---------------|------------|
| 200 | 2-3K | ~1% | Comfortable |
| 500 | 5-8K | ~3% | Comfortable |
| 1000 | 10-15K | ~7% | Ceiling |
| 2000+ | 20K+ | ~15%+ | Competes with work |

**Rule**: No single document should exceed 1000 lines.

## The Structural Affordances

Structure gives Claude handles on a document. Without structure, a document must be read in full. With structure, it can be read in parts.

### Elements That Enable Partial Reading

| Element | What It Provides |
|---------|------------------|
| **Headers** (`##`, `###`) | Section boundaries. Can skip irrelevant parts. |
| **Quick Reference at top** | May be sufficient. Can stop reading early. |
| **Tables** | Dense, scannable. 10 rows replaces 50 lines of prose. |
| **Pointers** (`See: other_doc.md`) | Modularity. Content lives elsewhere. |
| **Numbered sections** | Referenceable. "See Section 3" without re-reading. |
| **Table of Contents** | Overview of structure. Jump to relevant section. |

### Structure Requirements by Size

| Document Size | Structure Requirement |
|---------------|----------------------|
| < 200 lines | Optional but recommended |
| 200-500 lines | Headers required |
| 500-1000 lines | Headers + Quick Reference or TOC required |
| > 1000 lines | Should not exist. Split into multiple documents. |

**Rule**: Documents over 200 lines must have headers. Documents over 500 lines must have either a Quick Reference section at top or a Table of Contents.

## The Compression Principle

**Theory**: Everything should be as compressed as possible while still achieving its intent.

This is not a rule to enforce. It is a principle that shapes creation.

A document that could be 200 lines but is 500 lines has failed the compression principle. Not because 500 is too many, but because 300 lines exist without purpose.

Compression is not about arbitrary reduction. It is about: *Can this document still achieve its intent if made smaller?*

If yes, make it smaller.
If no, it is already at its proper size.

## RAG System Constraints

The RAG system chunks documents for embedding and retrieval. This adds constraints beyond the context window.

### Chunk Behavior

| Section Size | RAG Behavior |
|--------------|--------------|
| < 25 lines | May merge with adjacent chunks, loses boundary |
| 25-75 lines | Ideal. One section = one chunk |
| 75-150 lines | Gets split, structure helps maintain coherence |
| > 150 lines | Multiple chunks, may lose coherence |

### What RAG Needs From Documents

| Requirement | Why | How to Satisfy |
|-------------|-----|----------------|
| **Self-contained sections** | Chunks must make sense alone | Each section understandable without others |
| **Descriptive headers** | Headers become retrieval metadata | Headers should summarize section content |
| **Clear document metadata** | Propagates to all chunks | Title, purpose, source at top |
| **Natural chunk boundaries** | Better semantic coherence | Use headers, not arbitrary splits |

**Rule**: Sections should be 25-75 lines when possible. Each section should be understandable in isolation.

### Document Metadata for RAG

Every technology document should have at top:
- Title (becomes chunk metadata)
- Purpose (what this document achieves)
- Source/path (traceability)

---

## The Primitive Relationships

| Primitive | What It Is | Constraint |
|-----------|------------|------------|
| **Document** | exist-now (thing that exists) | Size in lines/tokens |
| **Reading** | do-now (action on document) | Context window capacity |
| **Chunking** | do-now (action on document) | RAG chunk size (25-75 lines ideal) |
| **Context Window** | Substrate (Claude's medium) | ~200K tokens, shared |
| **RAG System** | Substrate (retrieval medium) | Chunk size, self-containment |

The document exists. Reading and chunking happen. The context window and RAG system constrain what processing can handle.

## Enforcement (Hooks at Boundaries)

Claude writes documents. That's what Claude does. Don't change Claude's nature - transform at the boundary.

```
Claude writes → Hook transforms → RAG processes → Knowledge atoms extracted
(my nature)    (enforcement)     (its nature)    (output)
```

### The Principle

Each layer does what it does:
- Claude writes documents naturally
- Hook enforces constraints at the boundary
- RAG system processes what it receives
- Knowledge atom system extracts

Layers are decoupled. Boundaries do the translation.

### What the Hook Does

| Check | Action if Failed |
|-------|------------------|
| Line count > 1000 | Block or split |
| No headers and > 200 lines | Add headers or flag |
| Section > 150 lines | Flag for review |
| Missing metadata | Add default metadata |
| Non-self-contained sections | Flag for human review |

The hook transforms Claude's pattern into RAG's pattern. Claude doesn't think about RAG. RAG doesn't think about Claude. The hook handles the translation.

---

## Application

When creating a document:
1. What is its intent? (What must it achieve?)
2. What is its size? (Physical reality)
3. What is its structure? (Affordances for partial reading)
4. Can it be smaller? (Compression principle)

When a document exceeds 1000 lines:
- Split into multiple documents
- Or compress to essentials
- Do not publish as-is

---

*This document: ~190 lines. Intent: Capture knowledge about technology document primitives for the knowledge atom system.*
