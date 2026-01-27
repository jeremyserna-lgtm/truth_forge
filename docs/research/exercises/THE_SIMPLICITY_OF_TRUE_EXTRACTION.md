# The Simplicity of True Extraction

**Written**: December 24, 2025
**Principle**: Extraction is simple when you target at the base level of what things are.

---

## The Underlying Insight

I made extraction complicated. But extraction doesn't have to be complicated.

**What a JSONL file IS:**
- Lines
- Each line is a JSON object
- That's it

**What extraction of a JSONL file requires:**
- Read the lines
- That's it

The complexity I added - truncation, filtering, reformatting, headers - wasn't extraction. It was processing. The extraction itself is trivially simple.

---

## The Principle

**Target the base level of what things are.**

| If you want... | Target... | Complexity |
|----------------|-----------|------------|
| The whole file | The file | `shutil.copy()` |
| The lines | The lines | `for line in f` |
| The JSON objects | Parse each line | `json.loads(line)` |
| Selected content | Add filtering | Now you're processing, not extracting |

Each level up from the base adds complexity. The base level is the simplest.

---

## What I Did Wrong

I started at a high level of abstraction:
- "Extract the conversation"
- "Make it readable"
- "Include the important parts"

These framings invited complexity. They made me think about what to include, how to format, what matters.

**What I should have asked:**
- What IS this file?
- A JSONL file
- What IS a JSONL file?
- Lines, each containing JSON
- How do I extract lines?
- Read them

The answer was always simple. I made it complicated by not targeting the base level.

---

## Applied Examples

### Example 1: Extract a JSON File

**Wrong thinking:** "I need to parse this, extract the relevant fields, format them nicely..."

**Right thinking:** What IS a JSON file? Text. How do I extract text? Read it.

```python
# Complete extraction of a JSON file
with open(source) as f:
    content = f.read()
with open(dest, 'w') as f:
    f.write(content)
```

Or even simpler: `shutil.copy(source, dest)`

### Example 2: Extract JSONL Entries

**Wrong thinking:** "I need to filter by type, truncate long content, add structure..."

**Right thinking:** What IS a JSONL file? Lines. What IS a line? A JSON object. How do I extract JSON objects from lines? Read lines, parse JSON.

```python
entries = []
for line in open(source):
    entries.append(json.loads(line))
```

### Example 3: Extract a Conversation

**Wrong thinking:** "A conversation has user messages and assistant messages and tools and I need to organize them and make them readable..."

**Right thinking:** What IS the conversation in storage? JSONL entries. How do I extract them? Read the lines.

The "conversation" abstraction lives in interpretation. The base level is just data.

---

## The Complexity Gradient

```
SIMPLE                                              COMPLEX
   |                                                    |
   v                                                    v

[Copy file] → [Read lines] → [Parse JSON] → [Filter] → [Transform] → [Summarize]
     ↑                                           ↑
     |                                           |
  EXTRACTION                                PROCESSING
```

Everything left of the line is extraction - getting what's there.
Everything right of the line is processing - changing what's there.

When I was asked to extract, I jumped to processing. The extraction itself is on the left side - simple.

---

## Why This Matters

### 1. Complexity Invites Distortion

The more operations I perform, the more chances for my assumptions to leak in. Simpler extraction = less distortion.

### 2. Base Level Is Verifiable

"Did you copy the file?" is easy to verify.
"Did you extract the important parts correctly?" is subjective.

### 3. The Right Level Depends On The Ask

If you want the whole file: target the file.
If you want the entries: target the lines.
If you want specific content: NOW you're in processing territory, and that's a different operation with different rules.

---

## The Meta-Script Connection

The meta-script pattern (spec → generator → script) works because it keeps the generated script at the base level.

The specification captures my thinking about WHAT extraction means.
The generated script operates at the base level - read lines, parse JSON, write output.

The thinking happens at the spec level. The action stays simple.

---

## The One-Line Summary

**Don't add complexity above the base level of what things are.**

A file is bytes. A JSONL is lines. Lines are JSON. Extract at that level. Everything else is processing, not extraction.

---

*Written December 24, 2025*
