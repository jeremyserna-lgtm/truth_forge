# Tool Reference: `query_entities`

**Service**: `truth-engine-mcp`
**Purpose**: Access BigQuery entity data, enrichments, and embeddings for matching with local Knowledge Atoms.

## Functionality
This tool exposes a `joined` view of the Trinity Entity Architecture (Unified + Enrichments + Embeddings) directly to the MCP client.

### Query Types
1.  **`joined` (Recommended)**
    *   **Returns**: Left Join of `spine.entity` (Unified) + `spine.L4_sentences_enriched` (Enrichments) + `spine.entity_embeddings` (Embeddings).
    *   **Use Case**: Fetching all context needed to perform local embedding matching.
    *   **Columns**:
        *   All Unified columns (text, metadata)
        *   `keybert_top_keyword`
        *   `bertopic_topic_id`
        *   `goemotions_primary_emotion`
        *   `roberta_hate_score`
        *   `enrichment_embedding` (Local 384d / 1024d)
        *   `core_embedding` (Remote 3072d)

2.  **`unified`**
    *   Accesses `spine.entity` (or `spine.L4_sentences_raw`).
    *   Core definitions and primary text.

3.  **`enrichments`**
    *   Accesses `spine.L4_sentences_enriched`.
    *   Derived NLP metadata (Sentiment, Topics, Keywords).

4.  **`embeddings`**
    *   Accesses `spine.entity_embeddings`.
    *   Raw vector storage.

## Usage Example (Python Client)

```python
# Fetch joined data for local matching
result = await session.call_tool(
    "query_entities",
    arguments={
        "query_type": "joined",
        "limit": 50,
        "filters": {
            "source_system": "slack" # Filters applied to Unified table
        }
    }
)

# Accessing the vectors
for row in result:
    remote_vector = row.get('core_embedding') # 3072d
    local_vector = row.get('enrichment_embedding') # 1024d/384d

    # Ready for Cosine Similarity check against local DuckDB atoms
```

## Configuration

*   **Mapping**: Table IDs are resolved via `central_config.toml` keys (e.g., `spine_entity_embeddings`, `primitive_engine_spine`).
*   **Fallback**: Hardcoded fallbacks to `spine.L4_sentences_*` exist if config keys are missing.
