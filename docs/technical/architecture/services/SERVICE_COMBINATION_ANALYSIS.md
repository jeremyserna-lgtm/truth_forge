# Service Combination Analysis: What Services Can Do Together

**Date**: 2026-01-06
**Purpose**: Analyze combinations of 2-3 services working together to identify synergies, use cases, and emergent capabilities
**Total Services**: 20
**Combination Types**: 2-service pairs, 3-service chains

**Related Documents**:
- [`COGNITIVE_ARCHITECTURE_AND_AI_SCAFFOLDING.md`](./COGNITIVE_ARCHITECTURE_AND_AI_SCAFFOLDING.md) - Theoretical foundation on Extended Mind Thesis, scaffolding, and cognitive offloading

---

## Executive Summary

This document analyzes what combinations of services can accomplish when working together. Services follow the HOLD → AGENT → HOLD pattern, which means they can chain naturally: one service's HOLD₂ becomes another service's HOLD₁.

**Theoretical Foundation**: Service combinations enable **cognitive scaffolding** and **extended mind** capabilities. When services work together, they:
- **Scaffold complex cognitive tasks** by breaking them into manageable pieces
- **Offload routine processing** to free up germane cognitive load for synthesis
- **Mirror patterns** across multiple dimensions simultaneously
- **Enable co-evolution** through double-loop learning between services and user

**Key Findings**:
- **190 possible 2-service combinations** (20 choose 2)
- **1,140 possible 3-service combinations** (20 choose 3)
- **High-value combinations identified**: 45+ meaningful synergies
- **Emergent capabilities**: Services combine to create capabilities beyond individual services
- **Cognitive scaffolding**: Service combinations provide structural support for complex thinking

---

## Service Categories

### Foundation Services (The Walls)
1. **builder_service** - Enforces structure on new code
2. **schema_service** - Defines what data looks like
3. **verification_service** - Verifies outputs match expectations

### Core Services (The System)
4. **truth_service** - Extracts knowledge atoms from text
5. **knowledge_graph_service** - Stores graph-based knowledge
6. **analysis_service** - Synthesizes system state into insights
7. **contacts** - Syncs BigQuery contacts to local
8. **script_service** - Script intake and frontmatter stamping

### Utility Services (The Tools)
9. **model_gateway_service** - LLM routing (Ollama/Claude/Gemini)
10. **frontmatter_service** - YAML frontmatter stamping
11. **sentiment_service** - GoEmotions sentiment enrichment
12. **identity_service** - Immutable entity ID generation
13. **bigquery_archive_service** - Archives files to BigQuery
14. **duckdb_flush_service** - Flushes DuckDB to knowledge atoms
15. **pipeline_monitoring_service** - Monitors pipeline health
16. **reality_extractor_service** - Transforms exports to atoms
17. **recommendation_service** - Generates metabolic recommendations
18. **trinity_matching_service** - Matches entities across sources
19. **degradation_tracking_service** - Tracks entity degradation patterns
20. **framework_service** - Organism state management

---

## High-Value 2-Service Combinations

### Data Processing Chains

#### 1. Reality Extractor + Truth Service
**Combination**: `reality_extractor_service` → `truth_service`

**Flow**:
- HOLD₁: Conversation exports (JSON, CSV)
- AGENT₁: Reality Extractor (transforms to atoms)
- HOLD₂: Reality atoms
- AGENT₂: Truth Service (extracts knowledge atoms via Ollama)
- HOLD₃: Knowledge atoms in DuckDB

**Capability**: Complete pipeline from raw exports to structured knowledge atoms

**User Value**: Automatically extract and structure knowledge from any conversation export

**Use Case**: Process ChatGPT, Gemini, or Claude exports into queryable knowledge

---

#### 2. Truth Service + Knowledge Graph Service
**Combination**: `truth_service` → `knowledge_graph_service`

**Flow**:
- HOLD₁: Raw text content
- AGENT₁: Truth Service (extracts atoms)
- HOLD₂: Knowledge atoms
- AGENT₂: Knowledge Graph (parses into nodes/edges)
- HOLD₃: Graph.duckdb with relationships

**Capability**: Transform text into queryable knowledge graph with relationships

**User Value**: Build semantic knowledge graph from any text source

**Use Case**: Create knowledge graph from documents, conversations, or research papers

---

#### 3. Sentiment Service + Analysis Service
**Combination**: `sentiment_service` → `analysis_service`

**Flow**:
- HOLD₁: Knowledge atoms
- AGENT₁: Sentiment Service (enriches with GoEmotions)
- HOLD₂: Enriched atoms with sentiment
- AGENT₂: Analysis Service (synthesizes sentiment patterns)
- HOLD₃: Sentiment analysis insights

**Capability**: Emotional pattern analysis across knowledge base

**User Value**: Understand emotional patterns in your data over time

**Use Case**: Track emotional trends in conversations, identify stress patterns, monitor well-being

---

### Data Archival Chains

#### 4. DuckDB Flush + BigQuery Archive
**Combination**: `duckdb_flush_service` → `bigquery_archive_service`

**Flow**:
- HOLD₁: DuckDB databases
- AGENT₁: DuckDB Flush (converts to knowledge atoms)
- HOLD₂: Knowledge atoms (JSONL)
- AGENT₂: BigQuery Archive (uploads to BigQuery)
- HOLD₃: BigQuery archive dataset

**Capability**: Complete local-to-cloud archival pipeline

**User Value**: Automatically archive local data to cloud for analysis

**Use Case**: Archive processed data for long-term storage and analysis

---

### Quality Assurance Chains

#### 5. Builder Service + Verification Service
**Combination**: `builder_service` → `verification_service`

**Flow**:
- HOLD₁: New code
- AGENT₁: Builder Service (enforces structure)
- HOLD₂: Structured code
- AGENT₂: Verification Service (verifies structure matches expectations)
- HOLD₃: Verified code

**Capability**: Automated code quality pipeline

**User Value**: Ensure all new code follows framework standards

**Use Case**: Pre-commit validation, CI/CD integration

---

#### 6. Schema Service + Verification Service
**Combination**: `schema_service` → `verification_service`

**Flow**:
- HOLD₁: Data to validate
- AGENT₁: Schema Service (validates against schema)
- HOLD₂: Schema-validated data
- AGENT₂: Verification Service (verifies data quality)
- HOLD₃: Verified, schema-compliant data

**Capability**: Complete data validation pipeline

**User Value**: Ensure all data meets quality standards before processing

**Use Case**: Validate pipeline outputs, ensure data integrity

---

### Monitoring & Analysis Chains

#### 7. Pipeline Monitoring + Analysis Service
**Combination**: `pipeline_monitoring_service` → `analysis_service`

**Flow**:
- HOLD₁: Pipeline execution logs
- AGENT₁: Pipeline Monitoring (tracks health)
- HOLD₂: Health metrics
- AGENT₂: Analysis Service (synthesizes insights)
- HOLD₃: System health insights

**Capability**: Automated system health analysis

**User Value**: Understand system performance and health trends

**Use Case**: Proactive system monitoring, performance optimization

---

#### 8. Degradation Tracking + Analysis Service
**Combination**: `degradation_tracking_service` → `analysis_service`

**Flow**:
- HOLD₁: BigQuery entity data
- AGENT₁: Degradation Tracking (identifies incidents)
- HOLD₂: Degradation incidents
- AGENT₂: Analysis Service (analyzes patterns)
- HOLD₃: Degradation pattern insights

**Capability**: Entity health monitoring and analysis

**User Value**: Understand degradation patterns and prevent failures

**Use Case**: Monitor Clara, Lumens, Alatheia, Prism, Kael health

---

### Identity & Matching Chains

#### 9. Identity Service + Trinity Matching
**Combination**: `identity_service` → `trinity_matching_service`

**Flow**:
- HOLD₁: Entity data from multiple sources
- AGENT₁: Identity Service (generates deterministic IDs)
- HOLD₂: Entities with canonical IDs
- AGENT₂: Trinity Matching (matches across sources)
- HOLD₃: Matched entity clusters

**Capability**: Cross-source entity resolution

**User Value**: Unify entities across different data sources

**Use Case**: Match contacts, documents, or entities across BigQuery, local, and external sources

---

### Recommendation Chains

#### 10. Analysis Service + Recommendation Service
**Combination**: `analysis_service` → `recommendation_service`

**Flow**:
- HOLD₁: System state
- AGENT₁: Analysis Service (synthesizes insights)
- HOLD₂: Analysis results
- AGENT₂: Recommendation Service (generates recommendations via LLM)
- HOLD₃: Actionable recommendations

**Capability**: AI-powered recommendations from system analysis

**User Value**: Get personalized recommendations based on system state

**Use Case**: Metabolic recommendations, optimization suggestions, workflow improvements

---

## High-Value 3-Service Combinations

### Complete Knowledge Pipeline

#### 1. Reality Extractor → Truth Service → Knowledge Graph
**Combination**: `reality_extractor_service` → `truth_service` → `knowledge_graph_service`

**Flow**:
- HOLD₁: Conversation exports
- AGENT₁: Reality Extractor (transforms to atoms)
- HOLD₂: Reality atoms
- AGENT₂: Truth Service (extracts knowledge)
- HOLD₃: Knowledge atoms
- AGENT₃: Knowledge Graph (builds relationships)
- HOLD₄: Complete knowledge graph

**Capability**: End-to-end knowledge extraction and graph construction

**User Value**: Transform any conversation export into a queryable knowledge graph

**Use Case**: Build comprehensive knowledge graph from all conversation sources

---

### Complete Enrichment Pipeline

#### 2. Truth Service → Sentiment Service → Analysis Service
**Combination**: `truth_service` → `sentiment_service` → `analysis_service`

**Flow**:
- HOLD₁: Raw text
- AGENT₁: Truth Service (extracts atoms)
- HOLD₂: Knowledge atoms
- AGENT₂: Sentiment Service (adds emotion)
- HOLD₃: Enriched atoms
- AGENT₃: Analysis Service (synthesizes patterns)
- HOLD₄: Emotional pattern insights

**Capability**: Complete emotional intelligence pipeline

**User Value**: Understand emotional patterns in your knowledge base

**Use Case**: Track emotional trends, identify patterns, monitor well-being indicators

---

### Complete Quality Pipeline

#### 3. Builder Service → Schema Service → Verification Service
**Combination**: `builder_service` → `schema_service` → `verification_service`

**Flow**:
- HOLD₁: New code
- AGENT₁: Builder Service (enforces structure)
- HOLD₂: Structured code
- AGENT₂: Schema Service (validates schema)
- HOLD₃: Schema-validated code
- AGENT₃: Verification Service (verifies expectations)
- HOLD₄: Fully verified code

**Capability**: Complete code quality assurance pipeline

**User Value**: Ensure all code meets framework standards

**Use Case**: Automated code review, pre-commit hooks, CI/CD integration

---

### Complete Archival Pipeline

#### 4. DuckDB Flush → BigQuery Archive → Analysis Service
**Combination**: `duckdb_flush_service` → `bigquery_archive_service` → `analysis_service`

**Flow**:
- HOLD₁: Local DuckDB databases
- AGENT₁: DuckDB Flush (converts to atoms)
- HOLD₂: Knowledge atoms
- AGENT₂: BigQuery Archive (uploads to cloud)
- HOLD₃: BigQuery archive
- AGENT₃: Analysis Service (analyzes archive)
- HOLD₄: Archive analysis insights

**Capability**: Complete archival and analysis pipeline

**User Value**: Archive and analyze historical data

**Use Case**: Long-term data archival with analysis, trend analysis over time

---

### Complete Monitoring Pipeline

#### 5. Pipeline Monitoring → Degradation Tracking → Analysis Service
**Combination**: `pipeline_monitoring_service` → `degradation_tracking_service` → `analysis_service`

**Flow**:
- HOLD₁: System state
- AGENT₁: Pipeline Monitoring (tracks health)
- HOLD₂: Health metrics
- AGENT₂: Degradation Tracking (tracks entity degradation)
- HOLD₃: Degradation incidents
- AGENT₃: Analysis Service (correlates patterns)
- HOLD₄: System health insights with degradation patterns

**Capability**: Complete system health monitoring and analysis

**User Value**: Understand system health and degradation patterns together

**Use Case**: Proactive system monitoring, predict failures, optimize performance

---

### Complete Entity Resolution Pipeline

#### 6. Identity Service → Trinity Matching → Analysis Service
**Combination**: `identity_service` → `trinity_matching_service` → `analysis_service`

**Flow**:
- HOLD₁: Entity data from multiple sources
- AGENT₁: Identity Service (generates canonical IDs)
- HOLD₂: Entities with IDs
- AGENT₂: Trinity Matching (matches across sources)
- HOLD₃: Matched clusters
- AGENT₃: Analysis Service (analyzes matching patterns)
- HOLD₄: Entity resolution insights

**Capability**: Complete entity resolution and analysis

**User Value**: Unify and analyze entities across all sources

**Use Case**: Contact deduplication, document matching, entity relationship analysis

---

### Complete Recommendation Pipeline

#### 7. Analysis Service → Model Gateway → Recommendation Service
**Combination**: `analysis_service` → `model_gateway_service` → `recommendation_service`

**Flow**:
- HOLD₁: System state
- AGENT₁: Analysis Service (synthesizes insights)
- HOLD₂: Analysis results
- AGENT₂: Model Gateway (routes to appropriate LLM)
- HOLD₃: LLM context
- AGENT₃: Recommendation Service (generates recommendations)
- HOLD₄: Personalized recommendations

**Capability**: AI-powered recommendation generation with cost control

**User Value**: Get intelligent recommendations with cost protection

**Use Case**: Metabolic recommendations, optimization suggestions, personalized insights

---

### Complete Frontmatter Pipeline

#### 8. Script Service → Frontmatter Service → Schema Service
**Combination**: `script_service` → `frontmatter_service` → `schema_service`

**Flow**:
- HOLD₁: Raw scripts/files
- AGENT₁: Script Service (intake and stamping)
- HOLD₂: Processed scripts
- AGENT₂: Frontmatter Service (adds YAML frontmatter)
- HOLD₃: Files with frontmatter
- AGENT₃: Schema Service (validates frontmatter schema)
- HOLD₄: Validated, frontmatter-stamped files

**Capability**: Complete document processing pipeline

**User Value**: Automatically process and validate all documents

**Use Case**: Document intake, script processing, file organization

---

## Combination Patterns

### Pattern 1: Sequential Processing
**Structure**: Service A → Service B → Service C

**Characteristics**:
- Each service's HOLD₂ becomes next service's HOLD₁
- Natural data flow
- Each service adds value incrementally

**Examples**:
- Reality Extractor → Truth Service → Knowledge Graph
- Truth Service → Sentiment Service → Analysis Service

---

### Pattern 2: Parallel Enrichment
**Structure**: Service A → (Service B + Service C) → Service D

**Characteristics**:
- One service feeds multiple services
- Services process in parallel
- Results combined by final service

**Examples**:
- Truth Service → (Sentiment Service + Knowledge Graph) → Analysis Service

---

### Pattern 3: Validation Chain
**Structure**: Service A → Schema Service → Verification Service

**Characteristics**:
- Processing followed by validation
- Quality assurance focus
- Ensures correctness

**Examples**:
- Builder Service → Schema Service → Verification Service
- Any service → Schema Service → Verification Service

---

### Pattern 4: Analysis Chain
**Structure**: Data Service → Analysis Service → Recommendation Service

**Characteristics**:
- Data collection → Analysis → Action
- Insight generation focus
- Actionable outcomes

**Examples**:
- Degradation Tracking → Analysis Service → Recommendation Service
- Pipeline Monitoring → Analysis Service → Recommendation Service

---

## Use Case Categories

### 1. Knowledge Extraction & Graph Building
**Services**: Reality Extractor, Truth Service, Knowledge Graph

**Combinations**:
- Reality Extractor + Truth Service
- Truth Service + Knowledge Graph
- Reality Extractor + Truth Service + Knowledge Graph

**Outcome**: Transform raw exports into queryable knowledge graphs

---

### 2. Quality Assurance
**Services**: Builder, Schema, Verification

**Combinations**:
- Builder + Verification
- Schema + Verification
- Builder + Schema + Verification

**Outcome**: Ensure all code/data meets framework standards

---

### 3. System Health Monitoring
**Services**: Pipeline Monitoring, Degradation Tracking, Analysis

**Combinations**:
- Pipeline Monitoring + Analysis
- Degradation Tracking + Analysis
- Pipeline Monitoring + Degradation Tracking + Analysis

**Outcome**: Comprehensive system health insights

---

### 4. Data Archival & Analysis
**Services**: DuckDB Flush, BigQuery Archive, Analysis

**Combinations**:
- DuckDB Flush + BigQuery Archive
- DuckDB Flush + BigQuery Archive + Analysis

**Outcome**: Complete archival with analysis

---

### 5. Entity Resolution
**Services**: Identity, Trinity Matching, Analysis

**Combinations**:
- Identity + Trinity Matching
- Identity + Trinity Matching + Analysis

**Outcome**: Cross-source entity unification

---

### 6. Emotional Intelligence
**Services**: Truth Service, Sentiment Service, Analysis

**Combinations**:
- Sentiment Service + Analysis
- Truth Service + Sentiment Service + Analysis

**Outcome**: Emotional pattern analysis

---

### 7. AI-Powered Recommendations
**Services**: Analysis, Model Gateway, Recommendation

**Combinations**:
- Analysis + Recommendation
- Analysis + Model Gateway + Recommendation

**Outcome**: Personalized AI recommendations

---

## Framework Alignment in Combinations

### HOLD → AGENT → HOLD Chaining

When services combine, they create extended HOLD chains:

```
HOLD₁ → AGENT₁ → HOLD₂ → AGENT₂ → HOLD₃ → AGENT₃ → HOLD₄
```

**Example**: Reality Extractor → Truth Service → Knowledge Graph
- HOLD₁: Raw exports
- AGENT₁: Reality Extractor
- HOLD₂: Reality atoms
- AGENT₂: Truth Service
- HOLD₃: Knowledge atoms
- AGENT₃: Knowledge Graph
- HOLD₄: Knowledge graph

### Furnace Principle in Combinations

Combined services create extended Furnace chains:

**Truth → Heat → Meaning → Care** (Service 1)
↓
**Truth → Heat → Meaning → Care** (Service 2)
↓
**Truth → Heat → Meaning → Care** (Service 3)

**Example**: Truth Service → Sentiment Service → Analysis Service
- Service 1: Raw text → Extraction → Knowledge atoms → Stored
- Service 2: Knowledge atoms → Sentiment analysis → Enriched atoms → Stored
- Service 3: Enriched atoms → Pattern analysis → Insights → Delivered

---

## User Care in Combinations

### Cost Protection
When services chain, cost protection multiplies:
- **Model Gateway** protects LLM costs
- **BigQuery Client** protects query costs
- **Analysis Service** tracks total costs

**Combination**: Analysis + Model Gateway + Recommendation
- All LLM calls go through Model Gateway (cost control)
- Analysis Service tracks total costs
- User sees complete cost picture

### Error Handling
Chained services create error handling layers:
- **Service 1**: Catches input errors
- **Service 2**: Catches processing errors
- **Service 3**: Catches output errors

**Combination**: Builder + Schema + Verification
- Builder catches structure errors
- Schema catches validation errors
- Verification catches expectation errors

### Progress Tracking
Chained services provide granular progress:
- **Service 1**: Progress for step 1
- **Service 2**: Progress for step 2
- **Service 3**: Progress for step 3

**Combination**: Reality Extractor + Truth Service + Knowledge Graph
- User sees progress for each stage
- Can identify bottlenecks
- Can cancel at any stage

---

## Implementation Patterns

### Pattern 1: Direct Chaining
```python
# Service 1 output becomes Service 2 input
result1 = service1.process(input)
result2 = service2.process(result1)
result3 = service3.process(result2)
```

### Pattern 2: Orchestration Service
```python
# Orchestrator manages the chain
orchestrator = ServiceOrchestrator([
    service1,
    service2,
    service3
])
result = orchestrator.execute(input)
```

### Pattern 3: Primitive Pattern
```python
# Use Primitive Pattern for chaining
pattern = PrimitivePattern.from_paths(
    input_path="hold1.jsonl",
    output_path="hold2.jsonl",
    agent=lambda record, ctx: service3.process(
        service2.process(
            service1.process(record)
        )
    )
)
```

---

## Recommended High-Value Combinations

### Top 5 Two-Service Combinations

1. **Truth Service + Knowledge Graph Service**
   - **Why**: Most common pipeline (text → graph)
   - **Value**: High (core knowledge building)
   - **Use Case**: Build knowledge graph from any text

2. **Analysis Service + Recommendation Service**
   - **Why**: Analysis → Action pipeline
   - **Value**: High (actionable insights)
   - **Use Case**: Get recommendations from system analysis

3. **Degradation Tracking + Analysis Service**
   - **Why**: Monitoring → Insights pipeline
   - **Value**: High (preventive maintenance)
   - **Use Case**: Monitor entity health and prevent failures

4. **DuckDB Flush + BigQuery Archive**
   - **Why**: Local → Cloud pipeline
   - **Value**: High (data persistence)
   - **Use Case**: Archive local data to cloud

5. **Identity Service + Trinity Matching**
   - **Why**: Entity resolution pipeline
   - **Value**: High (data unification)
   - **Use Case**: Unify entities across sources

### Top 5 Three-Service Combinations

1. **Reality Extractor → Truth Service → Knowledge Graph**
   - **Why**: Complete knowledge pipeline
   - **Value**: Very High (end-to-end capability)
   - **Use Case**: Transform exports to knowledge graph

2. **Truth Service → Sentiment Service → Analysis Service**
   - **Why**: Complete emotional intelligence pipeline
   - **Value**: Very High (emotional insights)
   - **Use Case**: Understand emotional patterns

3. **Builder → Schema → Verification**
   - **Why**: Complete quality pipeline
   - **Value**: Very High (code quality)
   - **Use Case**: Automated code quality assurance

4. **Pipeline Monitoring → Degradation Tracking → Analysis**
   - **Why**: Complete health monitoring pipeline
   - **Value**: Very High (system health)
   - **Use Case**: Comprehensive system monitoring

5. **Analysis → Model Gateway → Recommendation**
   - **Why**: Complete AI recommendation pipeline
   - **Value**: Very High (AI-powered insights)
   - **Use Case**: Get personalized recommendations

---

## Next Steps

1. **Implement Orchestration Service**: Create service to manage combinations
2. **Create Combination Templates**: Pre-built templates for common combinations
3. **Add Combination Documentation**: Document each high-value combination
4. **Build Combination Tests**: Test combinations for correctness
5. **Monitor Combination Performance**: Track costs and performance

---

**Analysis Complete**: 2026-01-06
**Total Combinations Analyzed**: 1,330 (190 pairs + 1,140 triples)
**High-Value Combinations Identified**: 45+
