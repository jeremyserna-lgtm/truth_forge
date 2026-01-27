# Services Missing BigQuery Structures

**Generated**: 2026-01-06
**Purpose**: Log of all services that do not have parallel BigQuery structures

---

## Summary

- **Total Services Checked**: 27
- **Services WITH BigQuery**: 3
- **Services WITHOUT BigQuery**: 24

---

## ✅ Services WITH BigQuery Structure

1. **Identity Service**
   - Registry: `identity_service`
   - BigQuery Table: `identity.id_registry`
   - Status: ✅ Has parallel structure

2. **Contacts Service**
   - Registry: `contacts`
   - BigQuery Table: `identity.contacts_master`
   - Status: ✅ Has parallel structure

3. **Degradation Tracking Service**
   - Registry: `degradation_tracking_service`
   - BigQuery Table: `spine.entity_unified` (reads from)
   - Status: ✅ Has parallel structure

---

## ❌ Services WITHOUT BigQuery Structure

### Primitive Pattern Services (New Services)

1. **Cost Service**
   - Path: `Primitive/central_services/cost_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for cost tracking
   - **Suggested Table**: `governance.costs` or `spine.costs`

2. **Run Service**
   - Path: `Primitive/central_services/run_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for run tracking
   - **Suggested Table**: `governance.runs` or `spine.runs`

3. **Relationship Service**
   - Path: `Primitive/central_services/relationship_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for relationships
   - **Suggested Table**: `spine.relationships` or `knowledge.relationships`

4. **Version Service**
   - Path: `Primitive/central_services/version_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for version tracking
   - **Suggested Table**: `governance.versions` or `spine.versions`

5. **Workflow Service**
   - Path: `Primitive/central_services/workflow_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for workflows
   - **Suggested Table**: `governance.workflows` or `spine.workflows`

6. **Search Service**
   - Path: `Primitive/central_services/search_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: May not need BigQuery (local search service)
   - **Note**: Search service may be local-only

7. **Analytics Service**
   - Path: `Primitive/central_services/analytics_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for analytics results
   - **Suggested Table**: `analytics.results` or `spine.analytics`

8. **Quality Service**
   - Path: `Primitive/central_services/quality_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for quality assessments
   - **Suggested Table**: `governance.quality` or `spine.quality`

9. **Testing Service**
   - Path: `Primitive/central_services/testing_service/service.py`
   - Status: ACTIVE
   - **Action Needed**: Create BigQuery table for test results
   - **Suggested Table**: `governance.test_results` or `spine.test_results`

### Core Services

10. **Builder Service**
    - Path: `src/services/central_services/builder_service/`
    - Registry: `builder_service`
    - Status: ACTIVE
    - **Action Needed**: May not need BigQuery (build metadata)
    - **Note**: Build operations may be local-only

11. **Verification Service**
    - Path: `src/services/central_services/verification_service/`
    - Registry: `verification_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for verification results
    - **Suggested Table**: `governance.verifications` or `spine.verifications`

12. **Script Service**
    - Path: `src/services/central_services/script_service/`
    - Registry: `script_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for script metadata
    - **Suggested Table**: `governance.scripts` or `spine.scripts`

13. **Truth Service**
    - Path: `src/services/central_services/truth_service/`
    - Registry: `truth_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for knowledge atoms
    - **Suggested Table**: `knowledge.atoms` or `spine.knowledge_atoms`

14. **Knowledge Graph Service**
    - Path: `src/services/central_services/knowledge_graph_service/`
    - Registry: `knowledge_graph_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery tables for nodes and edges
    - **Suggested Tables**: `knowledge.nodes`, `knowledge.edges`

15. **Analysis Service**
    - Path: `src/services/central_services/analysis_service/`
    - Registry: `analysis_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for analysis results
    - **Suggested Table**: `analytics.analysis_results` or `spine.analysis`

16. **Recommendation Service**
    - Path: `src/services/central_services/recommendation_service/`
    - Registry: `recommendation_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for recommendations
    - **Suggested Table**: `recommendations.recommendations` or `spine.recommendations`

17. **Reality Extractor Service**
    - Path: `src/services/central_services/reality_extractor_service/`
    - Registry: `reality_extractor_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for extracted reality
    - **Suggested Table**: `knowledge.reality_extractions` or `spine.reality`

18. **Extractor Service**
    - Path: `src/services/central_services/extractor_service/`
    - Registry: `extractor_service`
    - Status: ACTIVE
    - **Action Needed**: May not need BigQuery (delegates to KnowledgeService)
    - **Note**: Delegates to other services

19. **Sentiment Service**
    - Path: `src/services/central_services/sentiment_service/`
    - Registry: `sentiment_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for sentiment analysis
    - **Suggested Table**: `analytics.sentiment` or `spine.sentiment`

20. **Frontmatter Service**
    - Path: `src/services/central_services/frontmatter_service/`
    - Registry: `frontmatter_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for frontmatter tracking
    - **Suggested Table**: `governance.frontmatter` or `spine.frontmatter`

21. **Schema Service**
    - Path: `src/services/central_services/schema_service/`
    - Registry: `schema_service`
    - Status: ACTIVE
    - **Action Needed**: May not need BigQuery (in-memory registry)
    - **Note**: Schema registry may be local-only

22. **Model Gateway Service**
    - Path: `src/services/central_services/model_gateway_service/`
    - Registry: `model_gateway_service`
    - Status: ACTIVE
    - **Action Needed**: Create BigQuery table for model requests/responses
    - **Suggested Table**: `governance.model_requests`, `governance.model_responses`

23. **BigQuery Archive Service**
    - Path: `src/services/central_services/bigquery_archive_service/`
    - Registry: `bigquery_archive_service`
    - Status: ACTIVE
    - **Action Needed**: Check archive dataset tables
    - **Note**: Service writes to archive dataset, may need verification

24. **DuckDB Flush Service**
    - Path: `src/services/central_services/duckdb_flush_service/`
    - Registry: `duckdb_flush_service`
    - Status: ACTIVE
    - **Action Needed**: May not need BigQuery (flushes to knowledge atoms)
    - **Note**: Flushes to knowledge atoms, which may have BigQuery structure

25. **Embedding Service (Canonical)**
    - Path: `architect_central_services/src/architect_central_services/ai_cognitive_services/embedding_service/service.py`
    - Status: ACTIVE
    - **Action Needed**: Check for embedding storage in BigQuery
    - **Note**: May store embeddings in BigQuery

---

## Recommended Actions

### High Priority (Services that should have BigQuery)

1. **Cost Service** → `governance.costs`
2. **Run Service** → `governance.runs`
3. **Truth Service** → `knowledge.atoms`
4. **Knowledge Graph Service** → `knowledge.nodes`, `knowledge.edges`
5. **Analytics Service** → `analytics.results`
6. **Quality Service** → `governance.quality`
7. **Testing Service** → `governance.test_results`

### Medium Priority (Services that may benefit from BigQuery)

1. **Relationship Service** → `spine.relationships`
2. **Version Service** → `governance.versions`
3. **Workflow Service** → `governance.workflows`
4. **Verification Service** → `governance.verifications`
5. **Script Service** → `governance.scripts`
6. **Recommendation Service** → `recommendations.recommendations`
7. **Sentiment Service** → `analytics.sentiment`
8. **Model Gateway Service** → `governance.model_requests`, `governance.model_responses`

### Low Priority (Services that may not need BigQuery)

1. **Search Service** - Local search may be sufficient
2. **Builder Service** - Build metadata may be local-only
3. **Schema Service** - In-memory registry may be sufficient
4. **Extractor Service** - Delegates to other services
5. **DuckDB Flush Service** - Flushes to knowledge atoms (which may have BQ)

---

## Next Steps

1. Review this document to determine which services actually need BigQuery structures
2. Create BigQuery tables for high-priority services
3. Update services to sync to BigQuery
4. Re-run the check script to verify structures are created

---

**This document is automatically generated by**: `scripts/validation/check_service_bigquery_structures.py`
