# Comprehensive Implementation Plan - Credential Bridge

**Date**: 2025-12-11
**Version**: 1.0.0
**Status**: AUTHORITATIVE CORE PLAN - SINGLE SOURCE OF TRUTH
**Purpose**: Complete implementation plan for Credential Bridge AI-powered credential intelligence platform

**THIS IS THE ONLY PLAN**: This document is the single authoritative source for all implementation. All other plans are deprecated or reference-only.

**Daily AI Budget**: **$25.00/day** | **Alert Threshold**: **$20.00/day (80%)**

**MANDATORY QUALITY REQUIREMENT**: All warnings and errors encountered during implementation MUST be addressed at their root cause. NO bypasses, workarounds, or shortcuts are permitted. See [Quality Requirements](#-mandatory-quality-requirements) section for details.

**LIVING PLAN**: This plan includes **feedback loops and adaptive reassessment** mechanisms. After each phase completion, the plan automatically reassesses priorities, dependencies, and effort estimates based on learnings.

---

## TABLE OF CONTENTS

1. [Executive Summary](#-executive-summary)
2. [Mandatory Quality Requirements](#-mandatory-quality-requirements)
3. [Implementation Workstreams](#-implementation-workstreams)
   - [Workstream 0: Foundation Hardening (COMPLETE)](#-workstream-0-foundation-hardening-complete)
   - [Workstream 1: Data Acquisition](#-workstream-1-data-acquisition)
   - [Workstream 2: AI Processing Pipeline](#-workstream-2-ai-processing-pipeline)
   - [Workstream 3: Product Development](#-workstream-3-product-development)
   - [Workstream 4: Customer Development](#-workstream-4-customer-development)
4. [Feedback Loops and Adaptive Reassessment](#-feedback-loops-and-adaptive-reassessment)
5. [Implementation Checklist](#-implementation-checklist)
6. [Success Metrics](#-success-metrics)
7. [Risk Mitigation](#-risk-mitigation)
8. [Documentation Index](#-documentation-index)

---

## MANDATORY QUALITY REQUIREMENTS

**CRITICAL**: This section applies to ALL implementation work. Read this before starting any service implementation.

### Root Cause Resolution Policy

**MANDATORY REQUIREMENT**: All warnings and errors encountered during implementation MUST be addressed at their root cause. NO bypasses, workarounds, or shortcuts are permitted.

#### What This Means

1. **All Warnings Must Be Fixed**
   - **FORBIDDEN**: Suppressing warnings with `# noqa`, `# type: ignore`, or similar
   - **FORBIDDEN**: Commenting out code that generates warnings
   - **FORBIDDEN**: Using `try/except: pass` to hide errors
   - **REQUIRED**: Fix the underlying issue causing the warning
   - **REQUIRED**: Understand why the warning exists
   - **REQUIRED**: Implement proper solution

2. **All Errors Must Be Fixed**
   - **FORBIDDEN**: Catching exceptions and ignoring them
   - **FORBIDDEN**: Using workarounds that mask the problem
   - **FORBIDDEN**: Adding "TODO: fix this later" comments
   - **REQUIRED**: Identify root cause of the error
   - **REQUIRED**: Implement proper fix
   - **REQUIRED**: Add tests to prevent regression

3. **All Linter Errors Must Be Fixed**
   - **FORBIDDEN**: Disabling linters for files
   - **FORBIDDEN**: Adding exceptions to linter config
   - **FORBIDDEN**: Using `# pylint: disable` without justification
   - **REQUIRED**: Fix code to pass all linter checks
   - **REQUIRED**: If linter rule is incorrect, fix the linter config (not the code)

4. **All Type Errors Must Be Fixed**
   - **FORBIDDEN**: Using `Any` type to bypass type checking
   - **FORBIDDEN**: Using `# type: ignore` without explanation
   - **FORBIDDEN**: Suppressing type errors
   - **REQUIRED**: Add proper type annotations
   - **REQUIRED**: Fix type mismatches
   - **REQUIRED**: Use proper type hints

5. **All Test Failures Must Be Fixed**
   - **FORBIDDEN**: Skipping failing tests
   - **FORBIDDEN**: Marking tests as expected failures
   - **FORBIDDEN**: Commenting out failing tests
   - **REQUIRED**: Fix the code causing test failures
   - **REQUIRED**: Update tests if requirements changed
   - **REQUIRED**: All tests must pass before completion

### Pre-Implementation Quality Checklist

**MANDATORY**: Before starting any new service or component, the following checklist **must be completed**:

1. **[ ] Test Strategy Documented**:
   - Document the strategy for testing edge cases, error handling paths, and external dependencies
   - The goal is to maintain **95% coverage** requirement

2. **[ ] Typing Strategy Confirmed**:
   - Confirm that all optional third-party dependencies will be handled using the `TYPE_CHECKING` and `Optional` pattern
   - Acknowledge the **zero-tolerance policy for `# type: ignore`** for any new code

3. **[ ] Governance Integration Plan**:
   - Identify where cost tracking will be applied
   - List the key operations that will be recorded to the audit trail

4. **[ ] Error Handling Plan**:
   - Define specific exception types for each failure mode
   - Plan retry logic with exponential backoff for external APIs

### Validation Requirements

Before marking any component as complete:

1. **Zero Warnings**: All warnings resolved
2. **Zero Errors**: All errors resolved
3. **Zero Linter Errors**: All linter checks pass (ruff, black, isort)
4. **Zero Type Errors**: All type checks pass (mypy)
5. **All Tests Pass**: 100% test pass rate
6. **95% Test Coverage Minimum**: Comprehensive test coverage required
7. **Root Cause Documented**: All fixes documented with root cause analysis
8. **Pre-commit Hooks Pass**: All pre-commit hooks pass on all files
9. **CI Pipeline Green**: All GitHub Actions workflows pass

---

## EXECUTIVE SUMMARY

### Current Implementation Status (2025-12-11)

**FOUNDATION COMPLETE**: Workstream 0 (Foundation Hardening) is **100% complete**. This establishes enterprise-grade infrastructure for all future development.

| Component | Status | Key Metrics |
|-----------|--------|-------------|
| **Test Coverage** | 96.77% | 820 tests passing |
| **Pre-commit Hooks** | Operational | black, isort, ruff, detect-secrets |
| **CI/CD Pipeline** | Operational | GitHub Actions, 95% coverage gate |
| **BigQuery Schema** | Defined | 7 migration files |
| **API Authentication** | Implemented | B2B API key auth + rate limiting |

### Business Context

**Credential Bridge** is an AI-powered credential data intelligence platform:

- **Data Source**: Credential Engine (1M+ credentials, free public API)
- **AI Processing**: Gemini Flash/Pro + Claude for CTDL parsing, enrichment, connections
- **Target Customers**: Niche.com, SchooLinks, Guild Education, State Workforce Boards
- **Moat**: CTDL expertise (6 years), AI-native architecture, domain knowledge

### Critical Dependency Chain

```
Foundation Hardening ✅
    ↓
Credential Engine Client (Workstream 1)
    ↓
AI Processing Pipeline (Workstream 2)
    ↓
API Product (Workstream 3)
    ↓
Customer Onboarding (Workstream 4)
```

### Budget Allocation ($25/day)

| Service | Daily Budget | Alert Threshold (80%) |
|---------|--------------|----------------------|
| **Global** | $25.00 | $20.00 |
| Gemini Flash | $10.00 | $8.00 |
| Gemini Pro | $5.00 | $4.00 |
| Claude (validation) | $3.00 | $2.40 |
| BigQuery | $2.00 | $1.60 |
| Other APIs | $5.00 | $4.00 |

---

## IMPLEMENTATION WORKSTREAMS

### WORKSTREAM 0: Foundation Hardening (COMPLETE)

**Status**: **100% COMPLETE**
**Duration**: 1 week
**Outcome**: Enterprise-grade foundation established

| Phase | Component | Status | Key Deliverables |
|-------|-----------|--------|------------------|
| **0.1** | Testing Framework | **COMPLETE** | 820 tests, 96.77% coverage, pytest fixtures |
| **0.2** | BigQuery Schema | **COMPLETE** | 7 migration files, credentials/institutions/outcomes tables |
| **0.3** | Pre-commit Hooks | **COMPLETE** | black, isort, ruff, detect-secrets, pytest |
| **0.4** | CI/CD Pipeline | **COMPLETE** | GitHub Actions, coverage gates, security scan |
| **0.5** | API Authentication | **COMPLETE** | B2B API key auth, rate limiting, dependency injection |

**Key Files Created**:
- [tests/conftest.py](tests/conftest.py) - Root test fixtures with LRU cache clearing
- [sql/migrations/](sql/migrations/) - 7 BigQuery DDL migration files
- [.pre-commit-config.yaml](.pre-commit-config.yaml) - Pre-commit configuration
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - CI/CD pipeline
- [src/credential_bridge/api/auth.py](src/credential_bridge/api/auth.py) - API authentication

---

### WORKSTREAM 1: Data Acquisition

**Status**: **NOT STARTED**
**Priority**: **HIGH** - Foundation for all product value
**Timeline**: 3 weeks

**Goal**: Acquire and normalize credential data from multiple sources, starting with Credential Engine.

#### Phase 1.1: Credential Engine Client Enhancement

**Week 1** | Priority: HIGH

**What It Accomplishes**:
- Reliable, production-ready access to 1M+ credentials from Credential Engine
- Proper CTDL parsing that extracts all valuable fields
- Rate limiting and retry logic to prevent API blocks
- Cost-effective pagination for bulk ingestion

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| CE Registry Client | Full API client with all endpoints | 100% API coverage |
| CTDL Parser | Parse CTDL JSON-LD to Pydantic models | All credential types handled |
| Rate Limiter | Token bucket rate limiting | No 429 errors in production |
| Pagination Handler | Handle large result sets | Process 10K+ credentials without timeout |

**Files to Create/Modify**:
- `src/credential_bridge/services/credential_engine.py` - Enhance existing client
- `src/credential_bridge/data/ctdl_parser.py` - NEW: CTDL parsing logic
- `tests/unit/services/test_credential_engine.py` - Comprehensive tests

**Quality Gates**:
- [ ] Test coverage 95%+
- [ ] All CTDL property types handled
- [ ] Rate limiting verified under load
- [ ] Documentation complete

#### Phase 1.2: State DOE Integration

**Week 2** | Priority: MEDIUM

**What It Accomplishes**:
- Access to state-specific credential data not in Credential Engine
- Florida as pilot state (Jeremy's expertise)
- Foundation for multi-state expansion

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| State Data Client | Generic client for state DOE APIs | Pluggable architecture |
| Florida Adapter | Florida-specific implementation | All FL credentials accessible |
| Data Normalizer | Normalize state data to common schema | Common Credential model |

**Files to Create**:
- `src/credential_bridge/services/state_data.py` - State data client
- `src/credential_bridge/services/adapters/florida.py` - FL-specific adapter
- `tests/unit/services/test_state_data.py` - Tests

#### Phase 1.3: IPEDS Institution Data

**Week 3** | Priority: MEDIUM

**What It Accomplishes**:
- Authoritative institution data from federal source
- Links credentials to accredited institutions
- Title IV eligibility for financial aid context

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| IPEDS Client | Client for IPEDS data access | All 7,000+ institutions |
| Institution Matcher | Match CE providers to IPEDS | >90% match rate |
| Data Pipeline | Automated IPEDS refresh | Monthly update pipeline |

**Files to Create**:
- `src/credential_bridge/services/ipeds.py` - IPEDS client
- `src/credential_bridge/pipelines/institution_pipeline.py` - Pipeline
- `tests/unit/services/test_ipeds.py` - Tests

---

### WORKSTREAM 2: AI Processing Pipeline

**Status**: **NOT STARTED**
**Priority**: **HIGH** - Core product differentiation
**Timeline**: 4 weeks

**Goal**: Build AI-powered processing pipeline that transforms raw credential data into actionable intelligence.

#### Phase 2.1: AI Service Foundation

**Week 4** | Priority: HIGH

**What It Accomplishes**:
- Unified interface for Gemini and Claude
- Cost tracking and budget enforcement
- Prompt versioning for reproducibility
- Response caching to minimize API costs

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| AI Orchestrator | Route requests to appropriate model | Model selection logic works |
| Cost Tracker | Track all AI API costs | Accurate cost attribution |
| Prompt Registry | Version-controlled prompts | All prompts versioned |
| Response Cache | Cache AI responses | >50% cache hit rate |

**Files to Create/Modify**:
- `src/credential_bridge/services/ai_service.py` - Enhance existing
- `src/credential_bridge/services/ai_cost_tracker.py` - NEW: Cost tracking
- `src/credential_bridge/services/prompt_registry.py` - NEW: Prompt management
- `tests/unit/services/test_ai_service.py` - Tests

#### Phase 2.2: CTDL Data Cleaning

**Week 5** | Priority: HIGH

**What It Accomplishes**:
- Clean and normalize messy credential descriptions
- Extract structured data from free-text fields
- Standardize provider names across sources
- Fill gaps in partial records

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| Description Cleaner | Clean HTML, normalize text | Clean descriptions |
| Entity Extractor | Extract entities (orgs, programs, requirements) | >85% precision |
| Provider Normalizer | Standardize provider names | Single canonical name per provider |
| Gap Filler | AI-powered field inference | >80% accuracy on validation set |

**Files to Create**:
- `src/credential_bridge/pipelines/cleaning_pipeline.py` - Cleaning pipeline
- `src/credential_bridge/services/entity_extractor.py` - Entity extraction
- `tests/unit/pipelines/test_cleaning_pipeline.py` - Tests

#### Phase 2.3: Connection Logic

**Week 6-7** | Priority: HIGH

**What It Accomplishes**:
- Link credentials to offering institutions
- Link credentials to occupation outcomes (SOC codes)
- Link credentials to industry demand (NAICS codes)
- Build the "connections" that make data valuable

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| Institution Linker | Link credentials to institutions | >90% accuracy |
| Occupation Mapper | Map to SOC codes | O*NET alignment |
| Industry Tagger | Tag with NAICS codes | Industry coverage |
| Confidence Scorer | Score all connections | Calibrated confidence |

**Files to Create**:
- `src/credential_bridge/pipelines/connection_pipeline.py` - Connection pipeline
- `src/credential_bridge/services/occupation_mapper.py` - SOC mapping
- `src/credential_bridge/services/industry_tagger.py` - NAICS tagging
- `tests/unit/pipelines/test_connection_pipeline.py` - Tests

#### Phase 2.4: Enrichment Pipeline

**Week 7** | Priority: MEDIUM

**What It Accomplishes**:
- Add labor market outcomes (wages, employment rates)
- Add cost and duration information
- Add quality signals (completion rates, accreditation)
- Full enrichment for API product

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| BLS Integration | Bureau of Labor Statistics data | Wage data for SOC codes |
| O*NET Integration | Occupation details | Skills, knowledge, abilities |
| Outcome Calculator | Compute outcome metrics | ROI estimates |

**Files to Create**:
- `src/credential_bridge/services/bls_client.py` - BLS API client
- `src/credential_bridge/services/onet_client.py` - O*NET client
- `src/credential_bridge/pipelines/enrichment_pipeline.py` - Enrichment

---

### WORKSTREAM 3: Product Development

**Status**: **NOT STARTED**
**Priority**: **HIGH** - Revenue generation
**Timeline**: 3 weeks

**Goal**: Build the API product that customers will pay for.

#### Phase 3.1: Search API

**Week 8** | Priority: HIGH

**What It Accomplishes**:
- Multi-faceted credential search
- Full-text search with relevance ranking
- Filter by state, type, provider, cost, duration
- Pagination and result limiting

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| Search Endpoint | POST /api/v1/credentials/search | <200ms p95 latency |
| Filter Engine | Multi-faceted filtering | All filters work |
| Ranking Algorithm | Relevance ranking | Relevant results first |
| Response Schema | Standardized response format | OpenAPI documented |

**Files to Create/Modify**:
- `src/credential_bridge/api/routes/credentials.py` - Search endpoint
- `src/credential_bridge/services/search_service.py` - Search logic
- `tests/integration/test_api.py` - API tests

#### Phase 3.2: Recommendation API

**Week 9** | Priority: MEDIUM

**What It Accomplishes**:
- AI-powered credential recommendations
- "Given this person, what credentials should they pursue?"
- Career pathway suggestions
- Prerequisite/stackable credential chains

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| Recommendation Endpoint | POST /api/v1/recommendations | Working recommendations |
| Profile Matcher | Match user profile to credentials | Relevant matches |
| Pathway Generator | Generate career pathways | Coherent pathways |

**Files to Create**:
- `src/credential_bridge/api/routes/recommendations.py` - Recommendation endpoint
- `src/credential_bridge/services/recommendation_service.py` - Recommendation logic

#### Phase 3.3: Analytics API

**Week 10** | Priority: MEDIUM

**What It Accomplishes**:
- Credential landscape analytics
- State-level credential gaps
- Provider comparison
- Market demand signals

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| Analytics Endpoint | GET /api/v1/analytics/{type} | Multiple analytics types |
| State Dashboard | State credential statistics | All 50 states |
| Gap Analysis | Identify credential gaps | Actionable insights |

**Files to Create**:
- `src/credential_bridge/api/routes/analytics.py` - Analytics endpoints
- `src/credential_bridge/services/analytics_service.py` - Analytics logic

---

### WORKSTREAM 4: Customer Development

**Status**: **NOT STARTED**
**Priority**: **HIGH** - Revenue validation
**Timeline**: Ongoing

**Goal**: Acquire first paying customers and validate product-market fit.

#### Phase 4.1: Pilot Customer (Niche.com)

**Week 11+** | Priority: HIGH

**What It Accomplishes**:
- First paying customer
- Product feedback loop
- Revenue validation
- Reference customer

**Key Deliverables**:
| Deliverable | Description | Success Criteria |
|-------------|-------------|------------------|
| Niche Integration | API integration with Niche | Working integration |
| Custom Endpoints | Niche-specific endpoints if needed | Meets their requirements |
| SLA Definition | Service level agreement | <200ms p95, 99.9% uptime |

**Activities**:
- [ ] Initial outreach to Niche product team
- [ ] Demo of credential search API
- [ ] Technical integration planning
- [ ] Contract negotiation
- [ ] Integration support

#### Phase 4.2: Expansion Customers

**Week 12+** | Priority: MEDIUM

**Target Customers**:
1. **SchooLinks** - K-12 career readiness platform
2. **Guild Education** - Tuition benefits provider (Denver connection)
3. **State Workforce Boards** - FL, IN, MI, CO

**Activities for Each**:
- [ ] Identify key contact
- [ ] Customize pitch for their use case
- [ ] Demo product
- [ ] Technical integration
- [ ] Contract and onboarding

---

## FEEDBACK LOOPS AND ADAPTIVE REASSESSMENT

### Living Plan Philosophy

**This plan is a living document** that adapts based on:
- Phase completion and learnings
- Customer feedback and requirements
- Cost and performance insights
- Market signals and priorities

### Feedback Loop Triggers

The plan automatically reassesses when:

1. **Phase Completion** - After each phase completes
2. **Customer Feedback** - When customer requirements change
3. **Cost Signals** - When cost anomalies are detected
4. **Performance Issues** - When performance degrades
5. **Weekly Review** - Every Monday

### Reassessment Process

#### Step 1: Capture Learnings

After each phase completion, capture:

```markdown
## Phase Completion Report: [Phase Name]

**Completion Date**: [Date]
**Actual Effort**: [Days] (vs. estimated [Days])
**Dependencies Discovered**: [List]
**Gaps Identified**: [List]
**Cost Impact**: [Costs]
**Customer Feedback**: [Feedback]
**Recommendations**: [Recommendations]
```

#### Step 2: Update Priorities

Reassess priorities based on:
1. **Customer Impact** - What customers are asking for
2. **Revenue Impact** - What generates revenue fastest
3. **Technical Dependencies** - What unblocks other work
4. **Cost Impact** - What reduces costs

#### Step 3: Adjust Implementation Order

Based on reassessment:
- **Promote** high-impact phases
- **Demote** lower-impact phases
- **Add** newly discovered requirements
- **Remove** features customers don't want

---

## IMPLEMENTATION CHECKLIST

### Workstream 0: Foundation (COMPLETE)
- [x] Testing framework established (96.77% coverage)
- [x] BigQuery schema defined (7 migrations)
- [x] Pre-commit hooks configured
- [x] CI/CD pipeline operational
- [x] API authentication implemented
- [x] **QUALITY**: All tests pass, all hooks pass

### Workstream 1: Data Acquisition
- [ ] Credential Engine client enhanced
- [ ] CTDL parser complete
- [ ] State data integration (Florida pilot)
- [ ] IPEDS institution data
- [ ] **QUALITY**: 95%+ test coverage, all quality gates pass

### Workstream 2: AI Processing
- [ ] AI service foundation complete
- [ ] CTDL data cleaning pipeline
- [ ] Connection logic (institution, occupation, industry)
- [ ] Enrichment pipeline (BLS, O*NET)
- [ ] **QUALITY**: 95%+ test coverage, cost tracking operational

### Workstream 3: Product Development
- [ ] Search API operational
- [ ] Recommendation API operational
- [ ] Analytics API operational
- [ ] OpenAPI documentation complete
- [ ] **QUALITY**: <200ms p95 latency, 95%+ test coverage

### Workstream 4: Customer Development
- [ ] Niche.com pilot integration
- [ ] First revenue generated
- [ ] SchooLinks integration
- [ ] Guild Education integration
- [ ] **QUALITY**: Customer satisfaction, SLA met

---

## SUCCESS METRICS

### Universal Quality Metrics (Apply to ALL Phases)

**MANDATORY**: All components must meet these quality metrics before completion:

- **Zero Warnings**: All warnings resolved at root cause
- **Zero Errors**: All errors resolved at root cause
- **Zero Linter Errors**: All linter checks pass
- **Zero Type Errors**: All type checks pass
- **100% Test Pass Rate**: All tests pass
- **95% Test Coverage Minimum**: Comprehensive test coverage required
- **No Bypasses**: No workarounds, shortcuts, or suppressions
- **Root Cause Documented**: All fixes documented with root cause analysis

### Business Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| **Credentials Indexed** | 100,000+ | Week 4 |
| **API Latency (p95)** | <200ms | Week 8 |
| **API Uptime** | 99.9% | Week 8 |
| **First Revenue** | $1,000+ MRR | Week 12 |
| **Customers** | 3+ paying | Week 16 |

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test Coverage** | 95%+ | pytest-cov |
| **API Response Time** | <200ms p95 | Monitoring |
| **AI Cost per Credential** | <$0.01 | Cost tracking |
| **Data Freshness** | <24 hours | Pipeline metrics |

---

## RISK MITIGATION

### High Risk Items

1. **Credential Engine API Changes**
   - **Risk**: CE changes API, breaks integration
   - **Mitigation**: Version pin API calls, monitor for changes
   - **Contingency**: Fallback to cached data, rapid adaptation

2. **AI Cost Overruns**
   - **Risk**: AI costs exceed budget
   - **Mitigation**: Strict cost tracking, budget alerts, caching
   - **Contingency**: Reduce processing scope, use cheaper models

3. **Customer Requirements Mismatch**
   - **Risk**: Build features customers don't want
   - **Mitigation**: Customer interviews before building
   - **Contingency**: Pivot based on feedback

### Medium Risk Items

1. **Performance Issues**
   - **Risk**: API too slow for production use
   - **Mitigation**: Performance testing early, caching strategy
   - **Contingency**: Add caching layers, optimize queries

2. **Data Quality Issues**
   - **Risk**: Source data too messy to use
   - **Mitigation**: Extensive cleaning pipeline, validation
   - **Contingency**: Manual curation for high-value credentials

---

## DOCUMENTATION INDEX

### Core Planning Documents

- **[COMPREHENSIVE_IMPLEMENTATION_PLAN.md](docs/COMPREHENSIVE_IMPLEMENTATION_PLAN.md)** (This Document) - Main implementation plan
- **[CLAUDE.md](CLAUDE.md)** - Project overview and AI guidance
- **[README.md](README.md)** - Project README

### Technical Documentation

- **[sql/migrations/](sql/migrations/)** - BigQuery schema migrations
- **[.github/workflows/ci.yml](.github/workflows/ci.yml)** - CI/CD pipeline
- **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Pre-commit configuration
- **[pyproject.toml](pyproject.toml)** - Python project configuration

### API Documentation

- **[src/credential_bridge/api/](src/credential_bridge/api/)** - API implementation
- OpenAPI spec (to be generated)

### Service Documentation

- **[src/credential_bridge/services/](src/credential_bridge/services/)** - Service implementations
- **[src/credential_bridge/pipelines/](src/credential_bridge/pipelines/)** - Pipeline implementations

---

## DEPRECATED PLANS

The following documents are **deprecated** and should not be used for implementation:

- **Foundation Hardening Plan** (`.claude/plans/cheeky-wondering-kite.md`): **DEPRECATED** - Workstream 0 is complete, use this plan instead

**All implementation must follow this COMPREHENSIVE_IMPLEMENTATION_PLAN.md**

---

**Change History**:
- **v1.0.0** (2025-12-11): Initial comprehensive implementation plan following Truth Engine pattern. Foundation hardening complete (96.77% coverage). Four workstreams defined: Data Acquisition, AI Processing, Product Development, Customer Development.

**Last Reassessment**: 2025-12-11
**Next Scheduled Reassessment**: After Workstream 1 Phase 1.1 completion
**Plan Version**: 1.0.0
