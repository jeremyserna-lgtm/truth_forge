# MCP Server: Knowledge Atom Access

**Purpose:** Enable AI to PULL context from knowledge atoms instead of Jeremy PUSHING documents.

---

## The Problem

**Current state (Push Model):**
```
Jeremy pushes documents → AI reads → AI asks questions → Jeremy answers
                              ↓
                    3+ hours per session
```

**Target state (Pull Model):**
```
AI queries knowledge atoms → Gets relevant context → Works immediately
                              ↓
                    Minutes, not hours
```

---

## Existing MCP Infrastructure

From `.mcp.json`, we already have:

| Server | What It Does |
|--------|--------------|
| `bigquery` | Generic BigQuery access |
| `truth-engine` | Primitive Engine access |
| `filesystem` | File read/write |
| `governance-middleware` | Cost enforcement |

**What's missing:** A semantic layer that understands knowledge atoms.

---

## Knowledge Atom Schema

**Table:** `truth_engine.knowledge_atoms`

| Field | Type | Description |
|-------|------|-------------|
| `atom_id` | STRING | Unique identifier |
| `content` | STRING | The knowledge content |
| `source_name` | STRING | Origin (conversation, document, code) |
| `created_at` | TIMESTAMP | When created |
| `embedding` | ARRAY<FLOAT64> | 3072-dim vector |
| `metadata` | JSON | Additional context |

**Related tables:**
- `entity_unified` - Canonical entities
- `entity_enrichments` - Derived features
- `entity_embeddings` - Vector search

---

## MCP Server Specification

### Server: `knowledge-atoms`

**Purpose:** Semantic access to knowledge base for AI context retrieval.

### Tools

#### 1. `search_atoms`

Search knowledge atoms by semantic similarity.

```typescript
interface SearchAtomsInput {
  query: string;           // Natural language query
  limit?: number;          // Max results (default: 10)
  source_filter?: string;  // Filter by source_name
  min_score?: number;      // Minimum similarity (0-1)
}

interface SearchAtomsOutput {
  atoms: Array<{
    atom_id: string;
    content: string;
    source_name: string;
    similarity: number;
    created_at: string;
  }>;
  total_count: number;
}
```

**Example:**
```
Tool: search_atoms
Input: { "query": "How does THE_PATTERN work?", "limit": 5 }
Output: Top 5 semantically similar knowledge atoms
```

#### 2. `get_context`

Get context for a specific topic across all sources.

```typescript
interface GetContextInput {
  topic: string;           // Topic to get context for
  depth?: "shallow" | "medium" | "deep";  // How much context
}

interface GetContextOutput {
  summary: string;         // AI-generated summary
  atoms: Array<Atom>;      // Supporting atoms
  related_topics: string[]; // Related topics to explore
}
```

**Example:**
```
Tool: get_context
Input: { "topic": "Federation System", "depth": "medium" }
Output: Summary + relevant atoms + related topics
```

#### 3. `verify_claim`

Verify a claim against the knowledge base.

```typescript
interface VerifyClaimInput {
  claim: string;           // Claim to verify
}

interface VerifyClaimOutput {
  verified: boolean;
  confidence: number;      // 0-1
  supporting_atoms: Array<Atom>;
  contradicting_atoms: Array<Atom>;
}
```

**Example:**
```
Tool: verify_claim
Input: { "claim": "Jeremy has 581 million entities in BigQuery" }
Output: { verified: true, confidence: 0.95, supporting: [...] }
```

#### 4. `exhale_learning`

Create a knowledge atom from the current session.

```typescript
interface ExhaleLearningInput {
  content: string;         // What was learned
  source_name: string;     // Source identifier
  category?: string;       // Category (pattern, insight, decision)
}

interface ExhaleLearningOutput {
  atom_id: string;
  federated: boolean;      // Whether it was sent to daughters
}
```

---

## Implementation Path

### Phase 1: Query Layer (Use existing BigQuery MCP)

Create SQL queries that AI can use via existing `bigquery` MCP:

```sql
-- Search atoms by keyword
SELECT atom_id, content, source_name, created_at
FROM `truth_engine.knowledge_atoms`
WHERE LOWER(content) LIKE LOWER('%{keyword}%')
ORDER BY created_at DESC
LIMIT 10;

-- Get recent atoms by source
SELECT * FROM `truth_engine.knowledge_atoms`
WHERE source_name = '{source}'
ORDER BY created_at DESC
LIMIT 20;
```

### Phase 2: Semantic Layer (New MCP Server)

Build `knowledge-atoms` MCP server with vector search:

```python
# mcp-servers/knowledge-atoms/src/knowledge_atoms/server.py

from mcp import Server, Tool
from google.cloud import bigquery

server = Server("knowledge-atoms")

@server.tool("search_atoms")
async def search_atoms(query: str, limit: int = 10):
    """Search knowledge atoms semantically."""
    # 1. Embed the query
    embedding = embed_text(query)

    # 2. Vector search in BigQuery
    results = vector_search(embedding, limit)

    # 3. Return formatted results
    return {"atoms": results}
```

### Phase 3: Context Synthesis

Add `get_context` that synthesizes multiple atoms:

```python
@server.tool("get_context")
async def get_context(topic: str, depth: str = "medium"):
    """Get synthesized context for a topic."""
    # 1. Search relevant atoms
    atoms = await search_atoms(topic, limit=20)

    # 2. Synthesize with LLM
    summary = synthesize(atoms, topic)

    # 3. Find related topics
    related = find_related(atoms)

    return {"summary": summary, "atoms": atoms, "related": related}
```

---

## Integration with Claude Code

### Configuration

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "knowledge-atoms": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "knowledge_atoms.server"],
      "cwd": "/Users/jeremyserna/Truth_Engine",
      "env": {
        "PYTHONPATH": "/Users/jeremyserna/Truth_Engine/mcp-servers/knowledge-atoms/src",
        "GOOGLE_APPLICATION_CREDENTIALS": "..."
      }
    }
  }
}
```

### Usage Pattern

AI session starts:
```
1. Read START_HERE.md (30 seconds)
2. Call get_context("current work") → Get recent context
3. Call verify_claim("is X real?") → Verify before doubting
4. Begin work with full context
```

**Result:** 3-hour verification → 3-minute context load

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Time to first useful work | 3+ hours | < 5 minutes |
| Questions AI asks | 10-20 | 2-3 |
| Documents Jeremy provides | 5-10 | 0 |
| Context accuracy | ~70% | ~95% |

---

## Status

| Component | Status |
|-----------|--------|
| Query Layer (Phase 1) | Ready (via bigquery MCP) |
| Semantic Layer (Phase 2) | Spec complete, needs implementation |
| Context Synthesis (Phase 3) | Spec complete, needs implementation |

---

## Related Documents

- `START_HERE.md` - AI onboarding
- `.mcp.json` - MCP configuration
- `docs/federation_learning/` - Federation protocol
- `Primitive/central_services/` - Knowledge atom services

---

*This solves Context Transfer Friction by letting AI PULL instead of Jeremy PUSH.*
