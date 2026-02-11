# THE PROMPTS

**Organized Prompt Registry**

**Author:** Jeremy Serna
**Date:** January 3, 2026
**Location:** Denver, Colorado
**Version:** 1.0

---

## WHY (Theory)

### Overview

All prompts used by THE_PRIMITIVE are organized into categories. Each prompt has an ID, function, and description.

**Usage in scripts:**
```python
result = prompt(content, task="CATEGORY.name")
```

### Categories

| Category | Purpose | LLM Required |
|----------|---------|--------------|
| CORE | Rule-based operations | No |
| EXTRACT | Membrane functions (knowledge atoms) | Yes |
| ANALYZE | Understanding content | Yes |
| GENERATE | Creating new content | Yes |
| TRANSFORM | Modifying content | Yes |
| CLASSIFY | Categorizing content | Yes |

---

## WHAT (Specification)

### CORE (Rule-based, No LLM)

These are not prompts. They are deterministic functions.

| ID | Function | Description | Implementation |
|----|----------|-------------|----------------|
| `CORE.hash` | `_hash()` | SHA256 of normalized content | `hashlib.sha256()` |
| `CORE.normalize` | `_normalize()` | Lowercase, collapse whitespace | String operations |
| `CORE.embed` | `_embed()` | Generate embedding vector | BGE-large / local model |
| `CORE.dedupe` | `dedupe()` | Check hash exists in store | Hash lookup |
| `CORE.similar` | `similar()` | Check cosine similarity > threshold | Vector math |

**These cannot be modified. They are locked in THE_PRIMITIVE.**

### EXTRACT (Membrane)

The membrane function. Respiration. Converts content to knowledge atoms.

| ID | Function | Description | Prompt |
|----|----------|-------------|--------|
| `EXTRACT.atoms` | `extract_knowledge_atoms()` | Extract truth as sentences | "Pull the truth from this as sentences." |

**This is THE prompt. The one that creates atoms. Everything goes through here.**

### ANALYZE

Understanding and evaluating content.

| ID | Function | Description | Prompt Pattern |
|----|----------|-------------|----------------|
| `ANALYZE.summarize` | `summarize()` | Condense to key points | "Summarize this content in {n} sentences." |
| `ANALYZE.review` | `review_output()` | Evaluate quality | "Review this output for {criteria}." |
| `ANALYZE.evaluate` | `evaluate()` | Score against criteria | "Evaluate this against: {criteria}" |
| `ANALYZE.compare` | `compare()` | Compare two contents | "Compare these two: {a} and {b}" |
| `ANALYZE.explain` | `explain()` | Explain for audience | "Explain this for {audience}." |
| `ANALYZE.critique` | `critique()` | Identify weaknesses | "What are the weaknesses in this?" |

### GENERATE

Creating new content from input.

| ID | Function | Description | Prompt Pattern |
|----|----------|-------------|----------------|
| `GENERATE.tags` | `generate_tags()` | Generate relevant tags | "Generate {n} tags for this content." |
| `GENERATE.metadata` | `extract_metadata()` | Extract structured metadata | "Extract metadata: title, type, audience, etc." |
| `GENERATE.title` | `generate_title()` | Generate a title | "Generate a title for this content." |
| `GENERATE.questions` | `generate_questions()` | Generate questions | "Generate {n} questions about this." |
| `GENERATE.outline` | `generate_outline()` | Generate an outline | "Create an outline for this content." |
| `GENERATE.followup` | `generate_followup()` | Generate follow-up items | "What follow-up actions are needed?" |

### TRANSFORM

Modifying content while preserving meaning.

| ID | Function | Description | Prompt Pattern |
|----|----------|-------------|----------------|
| `TRANSFORM.rewrite` | `rewrite()` | Rewrite in different style | "Rewrite this in {style} style." |
| `TRANSFORM.simplify` | `simplify()` | Make simpler | "Simplify this for a general audience." |
| `TRANSFORM.expand` | `expand()` | Add detail | "Expand on this with more detail." |
| `TRANSFORM.formalize` | `formalize()` | Make more formal | "Make this more formal/professional." |
| `TRANSFORM.translate` | `translate()` | Translate language | "Translate this to {language}." |
| `TRANSFORM.structure` | `structure()` | Add structure | "Add structure (headers, sections) to this." |

### CLASSIFY

Categorizing and labeling content.

| ID | Function | Description | Prompt Pattern |
|----|----------|-------------|----------------|
| `CLASSIFY.sentiment` | `classify_sentiment()` | Positive/negative/neutral | "Classify the sentiment: positive, negative, or neutral." |
| `CLASSIFY.topic` | `classify_topic()` | Topic classification | "Classify the topic from: {topics}" |
| `CLASSIFY.intent` | `classify_intent()` | User intent | "What is the intent: question, request, statement, etc." |
| `CLASSIFY.me_not_me` | `classify_me_not_me()` | Internal vs external | "Is this about ME (internal) or NOT ME (external)?" |
| `CLASSIFY.priority` | `classify_priority()` | Priority level | "Classify priority: critical, high, medium, low." |
| `CLASSIFY.actionable` | `classify_actionable()` | Actionable vs informational | "Is this actionable or informational?" |

---

## HOW (Reference)

### Implementation

Each prompt category lives in `claude_code_client.py`:

```python
# EXTRACT
def extract_knowledge_atoms(content: str) -> list[str]:
    """EXTRACT.atoms - THE membrane function."""
    return _call_claude(
        content=content,
        prompt="Pull the truth from this as sentences."
    )

# ANALYZE
def summarize(content: str, n: int = 3) -> str:
    """ANALYZE.summarize"""
    return _call_claude(
        content=content,
        prompt=f"Summarize this content in {n} sentences."
    )

# GENERATE
def generate_tags(content: str, n: int = 5) -> list[str]:
    """GENERATE.tags"""
    return _call_claude(
        content=content,
        prompt=f"Generate {n} tags for this content."
    )

# CLASSIFY
def classify_me_not_me(content: str) -> str:
    """CLASSIFY.me_not_me"""
    return _call_claude(
        content=content,
        prompt="Is this about ME (internal knowledge) or NOT ME (external/web)?"
    )
```

### Usage in THE_PRIMITIVE

```python
from THE_PRIMITIVE import prompt

# Use any prompt by category.name
result = prompt(content, task="ANALYZE.summarize")
result = prompt(content, task="GENERATE.tags")
result = prompt(content, task="CLASSIFY.me_not_me")

# The membrane function has its own call
atoms = extract_knowledge_atoms(content)  # EXTRACT.atoms
```

### Adding New Prompts

1. Determine category (ANALYZE, GENERATE, TRANSFORM, CLASSIFY)
2. Add to this table with ID, function, description, prompt pattern
3. Implement in `claude_code_client.py`
4. Test with THE_VALIDATOR

**New categories require framework discussion.**

### The Hierarchy

```
CORE (rule-based)
    │
    │ no LLM, deterministic
    │
EXTRACT (membrane)
    │
    │ THE prompt: "Pull the truth as sentences"
    │
├── ANALYZE (understand)
├── GENERATE (create)
├── TRANSFORM (modify)
└── CLASSIFY (categorize)
```

**CORE enables EXTRACT. EXTRACT enables everything else.**

---

*All prompts organized. Use by category.name. EXTRACT.atoms is THE membrane.*

— THE_FRAMEWORK

---

**END OF DOCUMENT**
