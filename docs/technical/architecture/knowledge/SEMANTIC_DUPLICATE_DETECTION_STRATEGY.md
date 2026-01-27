# Semantic Duplicate Detection Strategy

## Overview

We have **4,159 duplicate groups** (7,428 atoms) that are semantic duplicates - same meaning but different wording. Unlike exact duplicates (same text), these require semantic understanding to identify.

## Current State

- ✅ **Exact duplicates resolved**: 994 atoms deprecated
- ✅ **Embeddings available**: 20,596 atoms have embeddings stored
- ⚠️ **Semantic duplicates remaining**: 4,159 groups with same meaning, different wording
- ⚠️ **Embedding model unknown**: `embedding_model` field is NULL (embeddings exist but model not recorded)

## Semantic Matching Approaches

### Approach 1: Embedding Similarity (RECOMMENDED) ⭐

**How it works:**
- Use cosine similarity between embedding vectors
- Compare all atom pairs using BigQuery vector functions
- Threshold: 0.85-0.95 similarity = semantic duplicate

**Advantages:**
- ✅ Fast: O(n²) comparisons in BigQuery
- ✅ Already have embeddings (20,596 atoms)
- ✅ No additional API costs
- ✅ Can batch process efficiently

**Implementation:**
```sql
-- Use BigQuery ML.ML_DISTANCE for cosine similarity
SELECT
    a1.atom_id as atom1,
    a2.atom_id as atom2,
    ML.DISTANCE(a1.embedding, a2.embedding, 'COSINE') as similarity
FROM knowledge_atoms.knowledge_atoms a1
CROSS JOIN knowledge_atoms.knowledge_atoms a2
WHERE a1.status = 'active'
  AND a2.status = 'active'
  AND a1.atom_id < a2.atom_id  -- Avoid duplicate pairs
  AND a1.content != a2.content  -- Skip exact duplicates
HAVING similarity < 0.15  -- High similarity = low distance
```

**Challenges:**
- Need to know embedding model/dimensions
- Threshold tuning required (0.85 vs 0.90 vs 0.95)
- May miss nuanced differences

---

### Approach 2: Hybrid (Embeddings + Content Analysis)

**How it works:**
- Use embeddings for initial candidate pairs
- Add content-based filters (length, keywords, structure)
- Use LLM validation for high-confidence matches

**Advantages:**
- ✅ More accurate than embeddings alone
- ✅ Reduces false positives
- ✅ Can handle edge cases

**Implementation:**
```python
# Step 1: Find embedding-similar pairs
similar_pairs = find_similar_embeddings(threshold=0.90)

# Step 2: Filter by content similarity
content_similar = [
    pair for pair in similar_pairs
    if content_analysis_similar(pair)  # Length, keywords, etc.
]

# Step 3: LLM validation for top candidates
validated = llm_validate_semantic_duplicate(content_similar[:1000])
```

**Challenges:**
- More complex implementation
- Higher cost (LLM calls)
- Slower processing

---

### Approach 3: LLM-Based Direct Comparison

**How it works:**
- Compare atom pairs using LLM (e.g., Gemini Flash)
- Ask: "Do these two statements mean the same thing?"
- Binary classification: duplicate or not

**Advantages:**
- ✅ Most accurate
- ✅ Handles nuanced differences
- ✅ Can explain why they're duplicates

**Disadvantages:**
- ❌ Expensive: 4,159 groups × $0.001 = ~$4+
- ❌ Slow: Sequential processing
- ❌ Rate limits

**Implementation:**
```python
prompt = f"""Do these two knowledge statements mean the same thing?

Statement 1: {atom1_content}
Statement 2: {atom2_content}

Respond with JSON: {{"is_duplicate": true/false, "confidence": 0.0-1.0, "reason": "..."}}
"""

result = llm.generate(prompt)
```

---

### Approach 4: Clustering-Based

**How it works:**
- Cluster atoms by embedding similarity
- Within each cluster, identify semantic duplicates
- Process cluster-by-cluster (smaller search space)

**Advantages:**
- ✅ More efficient than pairwise comparison
- ✅ Groups related atoms together
- ✅ Can batch process clusters

**Implementation:**
```python
# Step 1: Cluster by embeddings
clusters = cluster_embeddings(k=1000, min_cluster_size=2)

# Step 2: Within each cluster, find semantic duplicates
for cluster in clusters:
    duplicates = find_duplicates_in_cluster(cluster)
    resolve_duplicates(duplicates)
```

---

## Recommended Approach: **Hybrid (Approach 2)**

### Phase 1: Embedding-Based Candidate Selection
1. Use BigQuery ML.DISTANCE for fast similarity search
2. Threshold: 0.90 cosine similarity (conservative)
3. Filter: Same knowledge_type, similar length (±20%)
4. Result: ~2,000-3,000 candidate pairs

### Phase 2: Content-Based Filtering
1. Keyword overlap check (≥60% shared keywords)
2. Length similarity check (ratio 0.7-1.3)
3. Structure similarity (both statements, both questions, etc.)
4. Result: ~1,500-2,000 high-confidence pairs

### Phase 3: LLM Validation (Optional)
1. Validate top 500 most confident pairs
2. Get LLM confirmation + confidence score
3. Use for threshold calibration

### Phase 4: Resolution
1. Auto-resolve high-confidence (similarity > 0.95)
2. Flag medium-confidence (0.90-0.95) for review
3. Manual review low-confidence (< 0.90)

---

## Implementation Plan

### Step 1: Verify Embedding Format
```python
# Check embedding dimensions and format
query = """
SELECT
    atom_id,
    content,
    ARRAY_LENGTH(embedding) as embedding_dim,
    embedding_model
FROM knowledge_atoms.knowledge_atoms
WHERE embedding IS NOT NULL
LIMIT 10
"""
```

### Step 2: Create Similarity Query
```python
# BigQuery vector similarity search
query = """
WITH active_atoms AS (
    SELECT
        atom_id,
        content,
        embedding,
        knowledge_type
    FROM knowledge_atoms.knowledge_atoms
    WHERE status = 'active'
      AND embedding IS NOT NULL
),
similarity_pairs AS (
    SELECT
        a1.atom_id as atom1_id,
        a2.atom_id as atom2_id,
        a1.content as atom1_content,
        a2.content as atom2_content,
        ML.DISTANCE(a1.embedding, a2.embedding, 'COSINE') as cosine_distance,
        1 - ML.DISTANCE(a1.embedding, a2.embedding, 'COSINE') as cosine_similarity
    FROM active_atoms a1
    CROSS JOIN active_atoms a2
    WHERE a1.atom_id < a2.atom_id
      AND a1.content != a2.content
      AND a1.knowledge_type = a2.knowledge_type
    HAVING cosine_similarity >= 0.90
)
SELECT * FROM similarity_pairs
ORDER BY cosine_similarity DESC
LIMIT 10000
"""
```

### Step 3: Content Filtering
```python
def filter_content_similarity(pairs):
    """Filter pairs by content characteristics"""
    filtered = []
    for pair in pairs:
        # Keyword overlap
        keywords1 = set(extract_keywords(pair['atom1_content']))
        keywords2 = set(extract_keywords(pair['atom2_content']))
        overlap = len(keywords1 & keywords2) / len(keywords1 | keywords2)

        # Length similarity
        len1, len2 = len(pair['atom1_content']), len(pair['atom2_content'])
        len_ratio = min(len1, len2) / max(len1, len2)

        if overlap >= 0.6 and len_ratio >= 0.7:
            filtered.append(pair)

    return filtered
```

### Step 4: Resolution
```python
def resolve_semantic_duplicates(similar_pairs):
    """Resolve semantic duplicates by keeping newest"""
    for pair in similar_pairs:
        # Get full atom details
        atom1 = get_atom(pair['atom1_id'])
        atom2 = get_atom(pair['atom2_id'])

        # Keep newest
        if atom1['extracted_at'] > atom2['extracted_at']:
            keep, deprecate = atom1, atom2
        else:
            keep, deprecate = atom2, atom1

        # Deprecate older
        deprecate_atom(
            atom_id=deprecate['atom_id'],
            reason=f"Semantic duplicate of {keep['atom_id']} (similarity: {pair['cosine_similarity']:.3f})",
            superseded_by=keep['atom_id']
        )
```

---

## Cost & Performance Estimates

### Embedding Similarity Only
- **Cost**: $0 (using existing embeddings)
- **Time**: ~5-10 minutes for 19,087 atoms
- **Accuracy**: ~85-90%

### Hybrid Approach
- **Cost**: $0 (embeddings) + ~$2-5 (optional LLM validation)
- **Time**: ~15-30 minutes
- **Accuracy**: ~90-95%

### LLM-Only Approach
- **Cost**: ~$10-20 (all pairs)
- **Time**: ~2-4 hours (rate limits)
- **Accuracy**: ~95-98%

---

## Next Steps

1. **Verify embeddings**: Check dimensions, model, format
2. **Run similarity query**: Find candidate pairs
3. **Analyze results**: Check false positive rate
4. **Tune threshold**: Adjust similarity cutoff
5. **Batch resolve**: Process in chunks (100 groups at a time)

Would you like me to start with Approach 1 (embedding similarity) and see what we find?
