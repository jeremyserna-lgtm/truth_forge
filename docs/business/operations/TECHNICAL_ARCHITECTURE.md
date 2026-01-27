# Technical Architecture

This document describes the technical architecture of Credential Bridge, including system components, data flow, and design decisions.

---

## Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Service Architecture](#service-architecture)
- [Data Architecture](#data-architecture)
- [Security Architecture](#security-architecture)
- [Governance Architecture](#governance-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Deployment Architecture](#deployment-architecture)

---

## System Overview

Credential Bridge is an AI-powered credential data intelligence platform that:

1. **Acquires** data from multiple sources (Credential Engine, IPEDS, State DOE, web scraping)
2. **Processes** data using AI for cleaning, normalization, and enrichment
3. **Stores** data in BigQuery with full-text search and governance tracking
4. **Delivers** intelligence via REST API with authentication and rate limiting

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
├─────────────────┬─────────────────┬─────────────────┬──────────────────────┤
│  Credential     │     IPEDS       │    State DOE    │   Institution        │
│  Engine API     │   (Federal)     │    (State)      │   Websites           │
└────────┬────────┴────────┬────────┴────────┬────────┴──────────┬───────────┘
         │                 │                 │                   │
         └─────────────────┴─────────────────┴───────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA ACQUISITION LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  CE Client      │  │  BLS Client     │  │  Guided Scraper │             │
│  │  (API Client)   │  │  (Wage Data)    │  │  (AI-Assisted)  │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
└───────────┴────────────────────┴────────────────────┴───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI PROCESSING LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  AI Service     │  │  Entity         │  │  Connection     │             │
│  │  (Gemini/Claude)│  │  Extraction     │  │  Inference      │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
└───────────┴────────────────────┴────────────────────┴───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA STORAGE LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          BigQuery                                    │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────────┐    │   │
│  │  │credentials│ │institutions│ │ outcomes │ │ governance tables│    │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API DELIVERY LAYER                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  FastAPI        │  │  Auth/Rate      │  │  Response       │             │
│  │  Application    │  │  Limiting       │  │  Caching        │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
└───────────┴────────────────────┴────────────────────┴───────────────────────┘
                                    │
                                    ▼
                           ┌───────────────┐
                           │   Customers   │
                           │   (B2B API)   │
                           └───────────────┘
```

---

## Component Architecture

### Core Package Structure

```
src/credential_bridge/
├── api/                    # API Layer
│   ├── main.py            # FastAPI application
│   ├── auth.py            # Authentication & rate limiting
│   └── routes/            # API endpoint handlers
│       ├── credentials.py # Search & retrieval
│       ├── recommendations.py # Personalized recommendations
│       └── analytics.py   # Usage & market analytics
│
├── core/                   # Core Infrastructure
│   ├── config.py          # Settings management (Pydantic)
│   ├── logging.py         # Structured logging
│   ├── errors.py          # Error handling & diagnostics
│   └── governance.py      # Cost tracking, audit, decorators
│
├── data/                   # Data Layer
│   └── models.py          # Pydantic data models
│
├── services/               # Business Logic
│   ├── ai_service.py      # AI orchestration (Gemini/Claude)
│   ├── search_service.py  # Search & caching
│   ├── recommendation_service.py  # Recommendation engine
│   ├── analytics_service.py # Analytics
│   ├── bigquery_service.py # Data persistence
│   ├── credential_engine.py # CE API client
│   ├── bls_client.py      # BLS API client
│   └── state_data.py      # State-specific data
│
└── pipelines/              # Data Pipelines
    ├── credential_pipeline.py  # Main ingestion pipeline
    └── scraping/           # Web scraping
        └── guided_scraper.py   # AI-assisted scraping
```

### Component Responsibilities

| Component | Responsibility | Key Classes |
|-----------|----------------|-------------|
| **api/** | HTTP layer, routing, validation | `FastAPI`, routers |
| **core/** | Cross-cutting concerns | `Settings`, `ErrorHandler`, `CostTracker` |
| **data/** | Data structures | `Credential`, `Institution`, `OccupationOutcome` |
| **services/** | Business logic | `SearchService`, `AIService`, `BigQueryService` |
| **pipelines/** | Data ingestion | `CredentialPipeline`, `GuidedScraper` |

---

## Data Flow

### Request Flow (API)

```
┌──────────┐    ┌─────────────┐    ┌───────────────┐    ┌─────────────┐
│  Client  │───▶│  FastAPI    │───▶│  Auth/Rate    │───▶│  Service    │
│  Request │    │  Router     │    │  Middleware   │    │  Layer      │
└──────────┘    └─────────────┘    └───────────────┘    └──────┬──────┘
                                                               │
                                                               ▼
┌──────────┐    ┌─────────────┐    ┌───────────────┐    ┌─────────────┐
│  Client  │◀───│  Response   │◀───│  Governance   │◀───│  BigQuery/  │
│  Response│    │  Formatting │    │  Tracking     │    │  Cache      │
└──────────┘    └─────────────┘    └───────────────┘    └─────────────┘
```

### Data Ingestion Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  External   │───▶│  Acquire    │───▶│  Clean &    │───▶│  AI Enrich  │
│  API        │    │  (Raw Data) │    │  Normalize  │    │  (Gemini)   │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Available  │◀───│  Index &    │◀───│  Validate   │◀───│  Connect    │
│  via API    │    │  Publish    │    │  (QA)       │    │  (Links)    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Technology Stack

### Runtime

| Layer | Technology | Purpose |
|-------|------------|---------|
| Language | Python 3.11+ | Primary runtime |
| Web Framework | FastAPI | REST API |
| Validation | Pydantic | Data validation |
| Async | asyncio | Async I/O |

### Data

| Layer | Technology | Purpose |
|-------|------------|---------|
| Database | BigQuery | Primary storage |
| Cache | In-memory (LRU) | Response caching |
| Search | BigQuery Search | Full-text search |

### AI

| Provider | Model | Use Case |
|----------|-------|----------|
| Google | Gemini 1.5 Flash | High-throughput processing |
| Anthropic | Claude 3.5 Sonnet | Complex reasoning |

### Infrastructure

| Layer | Technology | Purpose |
|-------|------------|---------|
| Cloud | Google Cloud Platform | Hosting |
| Compute | Cloud Run | API hosting |
| Data | BigQuery | Analytics warehouse |
| Monitoring | Cloud Logging | Observability |

### Development

| Tool | Purpose |
|------|---------|
| pytest | Testing |
| black | Formatting |
| ruff | Linting |
| mypy | Type checking |
| pre-commit | Git hooks |

---

## Service Architecture

### Service Layer Design

All services follow a consistent pattern:

```python
class ExampleService:
    """
    Service pattern:
    1. Singleton via get_X_service() function
    2. Injected settings
    3. Governance decorator for tracking
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        # Initialize dependencies

    @with_governance("operation_name")
    async def operation(self, request: RequestModel) -> ResponseModel:
        # Business logic
        pass


# Singleton accessor
_service: ExampleService | None = None

@lru_cache(maxsize=1)
def get_example_service() -> ExampleService:
    global _service
    if _service is None:
        _service = ExampleService()
    return _service

def reset_example_service() -> None:
    """Reset singleton for testing."""
    global _service
    _service = None
    get_example_service.cache_clear()
```

### Service Dependencies

```
┌────────────────┐
│   API Layer    │
└───────┬────────┘
        │
        ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ SearchService  │────▶│   AIService    │────▶│  Gemini/Claude │
└───────┬────────┘     └────────────────┘     └────────────────┘
        │
        ▼
┌────────────────┐     ┌────────────────┐
│BigQueryService │────▶│    BigQuery    │
└────────────────┘     └────────────────┘
```

### Key Services

#### AIService

Orchestrates AI calls with provider selection:

```python
class AIService:
    async def answer_credential_query(self, query: str) -> str:
        # Uses Gemini for speed

    async def complex_reasoning(self, context: str) -> str:
        # Uses Claude for depth

    async def enrich_credential(self, credential: Credential) -> Credential:
        # Uses Gemini for volume
```

#### SearchService

Handles credential search with caching:

```python
class SearchService:
    async def search(self, request: EnhancedSearchRequest) -> EnhancedSearchResponse:
        # Check cache first
        # Query BigQuery
        # Apply ranking
        # Return with facets

    async def get_similar(self, ctid: str) -> list[Credential]:
        # Similarity search
```

#### BigQueryService

Data persistence with governance:

```python
class BigQueryService:
    async def insert_credential(self, credential: Credential) -> str:
        # Insert with audit logging

    async def execute_query(self, query: str) -> QueryResult:
        # Execute with cost tracking
```

---

## Data Architecture

### BigQuery Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE TABLES                                     │
├─────────────────┬─────────────────┬─────────────────┬──────────────────────┤
│   credentials   │  institutions   │    outcomes     │       links          │
│   (1M+ rows)    │   (10K rows)    │   (500K rows)   │    (2M rows)         │
├─────────────────┼─────────────────┼─────────────────┼──────────────────────┤
│ - id            │ - id            │ - credential_id │ - credential_id      │
│ - ctid          │ - ipeds_id      │ - occupation_cd │ - institution_id     │
│ - name          │ - name          │ - median_wage   │ - confidence         │
│ - type          │ - state         │ - job_openings  │ - is_active          │
│ - provider      │ - type          │ - data_source   │ - program_url        │
│ - cost/duration │ - carnegie      │ - data_year     │ - effective_date     │
│ - occupations[] │ - accreditation │                 │                      │
│ - ingestion_dt  │ - ingestion_dt  │ - ingestion_dt  │ - ingestion_dt       │
└─────────────────┴─────────────────┴─────────────────┴──────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           GOVERNANCE TABLES                                  │
├─────────────────────────┬─────────────────────────┬────────────────────────┤
│     cost_tracking       │     audit_events        │    pipeline_runs       │
├─────────────────────────┼─────────────────────────┼────────────────────────┤
│ - cost_id               │ - event_id              │ - run_id               │
│ - run_id                │ - event_type            │ - pipeline_name        │
│ - operation             │ - operation             │ - status               │
│ - category              │ - run_id                │ - records_processed    │
│ - cost_usd              │ - details (JSON)        │ - total_cost_usd       │
│ - tokens_in/out         │ - success               │ - started_at           │
│ - timestamp             │ - timestamp             │ - ended_at             │
└─────────────────────────┴─────────────────────────┴────────────────────────┘
```

### Partitioning & Clustering

| Table | Partition By | Cluster By |
|-------|--------------|------------|
| credentials | ingestion_date | state, type, cip_code |
| institutions | ingestion_date | state, type |
| outcomes | ingestion_date | credential_id, occupation_code |
| cost_tracking | cost_date | category, run_id |
| audit_events | event_date | event_type, run_id |

### Search Indexes

```sql
CREATE SEARCH INDEX credentials_search_idx
ON credentials(name, description, keywords);
```

---

## Security Architecture

### Authentication

```
┌──────────┐    ┌─────────────┐    ┌───────────────┐
│  Client  │───▶│  X-API-Key  │───▶│  APIKeyStore  │
│  Request │    │  Header     │    │  Validation   │
└──────────┘    └─────────────┘    └───────┬───────┘
                                           │
                                           ▼
                                   ┌───────────────┐
                                   │  APIKeyInfo   │
                                   │  - key_id     │
                                   │  - customer   │
                                   │  - rate_limit │
                                   └───────────────┘
```

### Rate Limiting

```python
class RateLimiter:
    """In-memory sliding window rate limiter."""

    def check_limit(self, key_info: APIKeyInfo) -> tuple[bool, str]:
        # 1-minute sliding window
        # Per-key tracking
        # Returns (allowed, reason)
```

### API Key Tiers

| Tier | Rate Limit | Description |
|------|------------|-------------|
| Internal | 300/min | Development |
| Standard | 60/min | Default customers |
| Premium | 120/min | Premium customers |

---

## Governance Architecture

### Cost Tracking

Every AI/API call is tracked:

```python
@with_governance("search_credentials")
async def search(self, request):
    # Operation automatically tracked
    # Cost logged to BigQuery
    pass
```

### Audit Trail

All operations logged:

```python
audit(
    AuditEventType.DATA_ACCESS,
    "search_credentials",
    details={"query": query[:100]}
)
```

### Cost Protection

```python
# Settings
MAX_DAILY_AI_COST_USD = 10.0
MAX_QUERY_COST_USD = 1.0

# Enforcement
tracker = get_cost_tracker()
allowed, remaining = tracker.check_limits(estimated_cost)
if not allowed:
    raise CostLimitExceeded(remaining)
```

---

## Scalability Considerations

### Current Design (MVP)

| Component | Approach | Limit |
|-----------|----------|-------|
| API | Single instance | ~100 req/sec |
| Cache | In-memory | 1000 entries |
| Database | BigQuery | 10TB+ |
| AI | On-demand | API limits |

### Future Scaling

| Component | Scaling Strategy |
|-----------|------------------|
| API | Cloud Run auto-scaling |
| Cache | Redis cluster |
| Search | Vertex AI Search |
| AI | Vertex AI endpoints |

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Search p50 | <100ms | ~50ms |
| Search p95 | <200ms | ~150ms |
| Recommendation p50 | <500ms | ~300ms |
| Availability | 99.9% | - |

---

## Deployment Architecture

### Development

```bash
# Local development
uvicorn credential_bridge.api.main:app --reload
```

### Production (Planned)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Google Cloud Platform                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │ Cloud Run   │────▶│   BigQuery  │────▶│  Cloud      │                  │
│   │ (API)       │     │   (Data)    │     │  Logging    │                  │
│   └──────┬──────┘     └─────────────┘     └─────────────┘                  │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────┐     ┌─────────────┐                                       │
│   │ Cloud Load  │     │  Secret     │                                       │
│   │ Balancer    │     │  Manager    │                                       │
│   └─────────────┘     └─────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Push   │───▶│  Test   │───▶│  Build  │───▶│  Deploy │───▶│  Live   │
│  Code   │    │  (CI)   │    │  Image  │    │  (CD)   │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## Design Decisions

### Why FastAPI?

- Async native (good for I/O-bound operations)
- Automatic OpenAPI documentation
- Pydantic integration for validation
- High performance

### Why BigQuery?

- Serverless (no infrastructure management)
- Cost-effective for analytical queries
- Native search indexes
- Integrates with GCP ecosystem

### Why Gemini + Claude?

- Gemini: Fast, cost-effective for volume
- Claude: Better reasoning for complex tasks
- Flexibility to use best tool for each job

### Why Singleton Pattern?

- Efficient resource usage (one client per service)
- Easy to mock in tests (reset functions)
- Consistent with Python ecosystem patterns

### Why Governance Layer?

- Cost protection (prevent runaway AI costs)
- Audit trail (compliance, debugging)
- Operational visibility (what's happening)
