# Deep Dive: RAG + Knowledge Graphs (GraphRAG)
## Factual Grounding for Truth Engine

**Priority:** Strategic Foundation  
**Strategic Alignment:** The Spine, Entity Unified, Enrichments Layer  
**Created:** February 2026

---

## Executive Summary

GraphRAG combines Retrieval-Augmented Generation with Knowledge Graphs to reduce hallucinations by **70-90%** and enable multi-hop reasoning. For Truth Forge, this is the **natural evolution of The Spine**—your BigQuery entity triad already contains the raw material for a knowledge graph. GraphRAG turns The Spine from a data warehouse into an **active intelligence substrate**.

---

## What GraphRAG Actually Is

### The Problem with Basic RAG

Traditional RAG:
1. Chunks documents into vectors
2. Finds similar chunks via embedding search
3. Feeds chunks to LLM as context

**The limitation**: Chunks are isolated. Relationships are lost.

### What GraphRAG Adds

GraphRAG:
1. Extracts **entities** and **relationships** from documents
2. Stores in a **graph structure** (nodes and edges)
3. Retrieves via **graph traversal** (relationship paths)
4. Provides **connected context** to LLM

```
BASIC RAG                      GRAPHRAG
---------                      ----------
[Doc Chunk 1]                  [Entity] ──relates_to──▶ [Entity]
[Doc Chunk 2]        vs            │                       │
[Doc Chunk 3]                      ▼                       ▼
                               [Entity] ──caused_by──▶ [Entity]
```

---

## Your Current Architecture vs GraphRAG

### The Spine: What You Have

```
spine.entity_unified          spine.enrichments            spine.embeddings
├── entity_id                 ├── entity_id                ├── entity_id
├── source (claude_web...)    ├── sentiment_score          ├── gemini_3072
├── layer (L1-L8)             ├── topics                   ├── scout_1024
├── content                   ├── nrclex_emotions          └── ...
└── metadata                  └── ...
```

**You have entities. You have embeddings. You're missing: RELATIONSHIPS.**

### What GraphRAG Adds

```
spine.entity_unified
        │
        │ ◀─────────────────────────────────────────┐
        ▼                                           │
spine.entity_relationships  (NEW)                   │
├── source_entity_id ──────────────────────────────┤
├── target_entity_id ──────────────────────────────┘
├── relationship_type (references, contradicts, supports, causes)
├── confidence_score
└── extraction_method (llm, rule, manual)
```

---

## Implementation Strategy for Truth Forge

### Phase 1: Extract Relationships from Existing Entities (Week 1-2)

Use your existing entities to extract relationships:

```python
# spine/graph/relationship_extractor.py
from google.cloud import bigquery
import google.generativeai as genai

EXTRACTION_PROMPT = """
Given these two conversation excerpts, identify if there is a relationship between them.

EXCERPT A:
{entity_a}

EXCERPT B:
{entity_b}

If related, return JSON:
{
  "relationship_type": "references|contradicts|supports|causes|none",
  "confidence": 0.0-1.0,
  "explanation": "brief reason"
}

If not related, return: {"relationship_type": "none"}
"""

class RelationshipExtractor:
    def __init__(self):
        self.bq = bigquery.Client()
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Cost-efficient
    
    async def extract_for_entity(self, entity_id: str, top_k: int = 10):
        """Find relationships for one entity using embedding similarity + LLM verification."""
        
        # 1. Find candidate related entities via embedding similarity
        candidates = await self._find_similar_entities(entity_id, top_k)
        
        # 2. LLM verifies and classifies relationships
        relationships = []
        for candidate in candidates:
            result = await self._classify_relationship(entity_id, candidate)
            if result['relationship_type'] != 'none':
                relationships.append({
                    'source_entity_id': entity_id,
                    'target_entity_id': candidate['entity_id'],
                    'relationship_type': result['relationship_type'],
                    'confidence_score': result['confidence'],
                    'explanation': result['explanation']
                })
        
        return relationships
    
    async def _find_similar_entities(self, entity_id: str, top_k: int):
        """Use existing embeddings to find candidates."""
        query = f"""
        WITH source AS (
          SELECT gemini_3072 
          FROM `spine.embeddings` 
          WHERE entity_id = '{entity_id}'
        )
        SELECT 
          e.entity_id,
          e.content,
          COSINE_DISTANCE(source.gemini_3072, emb.gemini_3072) as distance
        FROM `spine.entity_unified` e
        JOIN `spine.embeddings` emb USING(entity_id)
        CROSS JOIN source
        WHERE e.entity_id != '{entity_id}'
        ORDER BY distance
        LIMIT {top_k}
        """
        return list(self.bq.query(query))
```

### Phase 2: Create Graph Schema in BigQuery (Week 3)

```sql
-- spine/schema/entity_relationships.sql
CREATE TABLE IF NOT EXISTS `spine.entity_relationships` (
  relationship_id STRING NOT NULL,
  source_entity_id STRING NOT NULL,
  target_entity_id STRING NOT NULL,
  relationship_type STRING NOT NULL,  -- references, contradicts, supports, causes
  confidence_score FLOAT64,
  explanation STRING,
  extraction_method STRING,  -- llm, rule, manual
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  
  -- For graph traversal optimization
  source_layer STRING,  -- L1-L8
  target_layer STRING,
  
  PRIMARY KEY (relationship_id) NOT ENFORCED
);

-- Index for fast graph traversal
CREATE SEARCH INDEX rel_source_idx ON `spine.entity_relationships`(source_entity_id);
CREATE SEARCH INDEX rel_target_idx ON `spine.entity_relationships`(target_entity_id);
```

### Phase 3: Build Graph Traversal Queries (Week 4)

```python
# spine/graph/traversal.py

class SpineGraph:
    def __init__(self):
        self.bq = bigquery.Client()
    
    def multi_hop_query(self, start_entity: str, hops: int = 2) -> dict:
        """
        Find all entities within N relationship hops.
        This is the core of GraphRAG.
        """
        query = f"""
        WITH RECURSIVE traversal AS (
          -- Base case: start entity
          SELECT 
            '{start_entity}' as entity_id,
            0 as depth,
            CAST(NULL AS STRING) as relationship_type,
            ARRAY<STRING>['{start_entity}'] as path
          
          UNION ALL
          
          -- Recursive case: follow relationships
          SELECT 
            r.target_entity_id,
            t.depth + 1,
            r.relationship_type,
            ARRAY_CONCAT(t.path, [r.target_entity_id])
          FROM traversal t
          JOIN `spine.entity_relationships` r 
            ON t.entity_id = r.source_entity_id
          WHERE t.depth < {hops}
            AND r.target_entity_id NOT IN UNNEST(t.path)  -- Avoid cycles
        )
        SELECT DISTINCT
          entity_id,
          depth,
          relationship_type,
          path
        FROM traversal
        ORDER BY depth
        """
        return list(self.bq.query(query))
    
    def find_contradictions(self, entity_id: str) -> list:
        """Find all entities that contradict a given entity."""
        query = f"""
        SELECT 
          e.*,
          r.confidence_score,
          r.explanation
        FROM `spine.entity_relationships` r
        JOIN `spine.entity_unified` e 
          ON r.target_entity_id = e.entity_id
        WHERE r.source_entity_id = '{entity_id}'
          AND r.relationship_type = 'contradicts'
        ORDER BY r.confidence_score DESC
        """
        return list(self.bq.query(query))
```

### Phase 4: GraphRAG Retrieval (Week 5-6)

Combine graph traversal with traditional RAG:

```python
# truth_engine/rag/graph_rag.py

class GraphRAGRetriever:
    def __init__(self):
        self.graph = SpineGraph()
        self.embeddings = EmbeddingClient()
        self.bq = bigquery.Client()
    
    async def retrieve(self, query: str, k: int = 10) -> dict:
        """
        Hybrid retrieval: embeddings + graph traversal.
        """
        # 1. Vector retrieval (traditional RAG)
        query_embedding = await self.embeddings.embed(query)
        similar_entities = await self._vector_search(query_embedding, k)
        
        # 2. Graph expansion (GraphRAG addition)
        expanded_context = []
        for entity in similar_entities[:3]:  # Top 3 seeds
            # Get 2-hop neighborhood
            neighbors = self.graph.multi_hop_query(entity['entity_id'], hops=2)
            expanded_context.extend(neighbors)
        
        # 3. Combine and deduplicate
        all_entities = self._deduplicate(similar_entities + expanded_context)
        
        # 4. Build context with relationship metadata
        context = self._build_context_with_relationships(all_entities)
        
        return {
            'entities': all_entities,
            'context': context,
            'retrieval_trace': {
                'vector_hits': len(similar_entities),
                'graph_expansion': len(expanded_context),
                'total': len(all_entities)
            }
        }
    
    def _build_context_with_relationships(self, entities: list) -> str:
        """Build LLM context that includes relationship information."""
        context = "KNOWLEDGE CONTEXT:\n\n"
        
        for entity in entities:
            context += f"[Entity {entity['entity_id']}]\n"
            context += f"Content: {entity['content']}\n"
            
            if entity.get('relationship_type'):
                context += f"Relationship: {entity['relationship_type']} "
                context += f"(from entity in path)\n"
            
            context += "\n"
        
        return context
```

---

## Practical Next Steps

### Immediate (This Week)

1. **Analyze Existing Entity Connections**
   ```sql
   -- How many entities share topics?
   SELECT 
     a.entity_id as entity_a,
     b.entity_id as entity_b,
     ARRAY_LENGTH(
       ARRAY(SELECT * FROM UNNEST(a.topics) 
             INTERSECT DISTINCT 
             SELECT * FROM UNNEST(b.topics))
     ) as shared_topics
   FROM `spine.enrichments` a, `spine.enrichments` b
   WHERE a.entity_id < b.entity_id
   ORDER BY shared_topics DESC
   LIMIT 100;
   ```

2. **Prototype Relationship Extraction**
   Run extraction on 100 entities to validate the approach.

3. **Design Relationship Types**
   - `references`: One entity mentions content from another
   - `contradicts`: Entities assert opposite claims
   - `supports`: One entity provides evidence for another
   - `causes`: Temporal/causal relationship
   - `elaborates`: One entity expands on another

### Short-Term (Next 2 Weeks)

4. **Create Relationship Table**
   Implement the SQL schema above.

5. **Batch Extraction Pipeline**
   Build pipeline to extract relationships for all 11.8M entities (prioritize high-value entities first).

6. **Test Multi-Hop Queries**
   Validate that relationship traversal improves answer quality.

### Medium-Term (Next Month)

7. **Integrate with Truth Engine**
   Replace simple embedding retrieval with GraphRAG.

8. **Build Contradiction Detection**
   Automatically flag entities that contradict each other.

9. **Visualize the Graph**
   Create a visualization tool for exploring entity relationships.

---

## Key Learnings for Your Architecture

### 1. The Spine is 80% of a Knowledge Graph

You already have:
- ✅ Entities (entity_unified)
- ✅ Properties (enrichments)
- ✅ Embeddings for similarity
- ❌ Explicit relationships (this is what to add)

### 2. Relationships Enable Contradiction Detection

With relationships, you can automatically detect:
- Claims that contradict each other
- Claims that lack supporting evidence
- Circular reasoning chains

**This powers Fracture Protocol at scale.**

### 3. Graph Traversal Replaces Keyword Search

Instead of "find documents mentioning X", you can:
- "Find everything that contradicts X"
- "Find the sources that support X"
- "Trace the reasoning chain from A to B"

### 4. BigQuery Supports Graph Queries

You don't need a separate graph database. BigQuery's recursive CTEs (Common Table Expressions) handle graph traversal for your scale.

---

## Metrics to Track

| Metric | Current (Estimated) | Target (GraphRAG) |
|--------|---------------------|-------------------|
| Hallucination rate | ~15-20% | <5% |
| Context relevance | Embedding only | Embedding + relationship |
| Multi-hop reasoning | Not possible | 2-3 hop queries |
| Contradiction detection | Manual | Automatic |
| Answer with citations | Partial | 100% |

---

## Risk Considerations

| Risk | Mitigation |
|------|------------|
| Relationship extraction quality | Start with high-confidence rules; human review sample |
| Compute cost for 11.8M entities | Prioritize high-value entities; batch processing |
| Graph becomes unwieldy | Prune low-confidence edges; hierarchical views |
| Query latency | Index optimization; caching frequent paths |

---

## Connection to Truth Forge Vision

GraphRAG transforms The Spine from data storage to **active intelligence**:

> "The Spine doesn't just hold knowledge—it understands how knowledge connects, contradicts, and supports itself."

**Without GraphRAG**: You retrieve similar documents.  
**With GraphRAG**: You retrieve the complete reasoning context.

---

## Resources

- **Microsoft GraphRAG**: https://github.com/microsoft/graphrag
- **Neo4j GraphRAG**: https://neo4j.com/blog/graphrag/
- **BigQuery Graph Queries**: https://cloud.google.com/bigquery/docs/recursive-ctes
- **Stardog Enterprise**: https://www.stardog.com/platform/
- **LangChain GraphRAG**: https://python.langchain.com/docs/modules/data_connection/retrievers/self_query

---

*Deep Dive Document 4 of 6 — GraphRAG Implementation*
