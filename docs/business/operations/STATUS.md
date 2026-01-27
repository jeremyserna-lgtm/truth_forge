# Credential Bridge (Credential Atlas): Current Status

**Last Updated**: December 28, 2025

**Website**: https://credentialatlas.com
**API**: https://api.credentialatlas.com
**GCP Project**: `credential-bridge`

---

## Executive Summary

The infrastructure is built. The data is loaded. The code is tested. What's missing: customers.

**Next action**: Send 10 emails. Close one.

---

## Data Infrastructure (Live in BigQuery)

| Table | Records | Purpose |
|-------|---------|---------|
| `ipeds_completions` | 303,292 | National completion data |
| `scorecard_programs` | 213,711 | College Scorecard program earnings |
| `bls_occupation_wages` | 34,554 | Wage data by occupation/state |
| `workforce_credentials` | 32,400 | Workforce credentials |
| `state_credentials` | 15,880 | State-level credentials |
| `national_credentials` | 7,956 | Aggregated credential intelligence |
| `ipeds_institutions` | 6,163 | All US institutions |
| `cip_soc_crosswalk` | 6,097 | Education-to-Occupation links |

**Key Metrics**:
- 10.8M total completions tracked
- 93% of credentials have wage data
- 44% have Scorecard earnings data
- 868 occupations linked

---

## Code Infrastructure

### Services (24 files in `src/credential_bridge/services/`)

| Service | Purpose |
|---------|---------|
| `ai_service.py`, `ai_orchestrator.py` | AI orchestration (Gemini, Claude) |
| `bigquery_service.py` | Data persistence |
| `credential_engine.py` | CTDL/Registry API integration |
| `ipeds.py`, `bls_client.py`, `onet_client.py` | Data source clients |
| `search_service.py`, `matching_service.py` | Search and matching |
| `identity_service.py` | ID generation (adapted from Truth Engine) |
| `analytics_service.py`, `recommendation_service.py` | Intelligence layer |
| `scorecard_client.py` | College Scorecard integration |
| `state_data.py` | State-specific credential rules |

### Scripts (17 files in `scripts/`)

- IPEDS ingestion, BLS wages, College Scorecard loading
- State data collection (enterprise-grade with retry, dedup, audit)
- CIP-SOC crosswalk loading from NCES
- National credential generation and aggregation

### API (`src/credential_bridge/api/`)

- FastAPI application with OpenAPI docs
- Routes: credentials, recommendations, analytics, state data, natural language queries
- Authentication middleware with rate limiting

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 0.4.0 | Dec 14, 2025 | Identity layer, API clients, entity registry |
| 0.3.0 | Dec 14, 2025 | National credentials, BLS wages, CIP-SOC crosswalk |
| 0.2.0 | Dec 11, 2025 | Foundation hardening, 220+ tests, CI/CD |
| 0.1.0 | Dec 1, 2025 | Core infrastructure, API, services |

---

## What's Built vs What's Pending

### Built

**Data Infrastructure**:
- [x] Complete data pipeline (IPEDS, BLS, Scorecard, CIP-SOC)
- [x] 600K+ records in BigQuery
- [x] GCP project configured (`credential-bridge`)

**Code**:
- [x] API infrastructure (FastAPI)
- [x] AI orchestration services (Gemini, Claude)
- [x] Identity service with deterministic IDs
- [x] 24 service modules
- [x] 17 data ingestion scripts
- [x] Pre-commit hooks, CI/CD pipeline
- [x] 220+ tests with 80%+ coverage

**Business**:
- [x] Domain purchased (credentialatlas.com)
- [x] Business plan and financials (Year 1: $303K → Year 3: $2.65M)
- [x] Target customer list (10 companies with contacts)
- [x] Email outreach template
- [x] Competitive analysis complete

### Blockers Before Outreach

| Blocker | Status | Action | Cost |
|---------|--------|--------|------|
| **LLC** | **DONE** | Credential Atlas LLC (SOS ID: 20258406582) | $50 paid 12/28/2025 |
| **Website** | "Coming Soon" placeholder on Squarespace | Build out landing page with value prop | ~$16/mo Squarespace |

### Pending (After First Customer)

- [ ] API deployed to Cloud Run (production)
- [ ] First paying customer
- [ ] Case studies / testimonials
- [ ] Business bank account
- [ ] GraphQL endpoint
- [ ] Webhook notifications

---

## Immediate Next Steps

1. **Form Colorado LLC** ($50, ~15 minutes online)
   - Go to: https://www.sos.state.co.us
   - Name: "Credential Atlas LLC" or similar
   - You can be your own registered agent

2. **Build Website** (credentialatlas.com)
   - Currently: Squarespace "Coming Soon" page
   - Need: Landing page with value proposition, contact form
   - Keep it simple: who you are, what you do, how to reach you

3. **Send 10 Emails**
   - Prospects ready in `docs/business/PROSPECT_LIST.md`
   - Template ready
   - Close one

---

## The Business Model

**Core Value Proposition**:
Organizations need credential data connected to institutional context and labor market outcomes. Currently fragmented across multiple sources. AI can do in 2-4 weeks what used to take 6 months with a team of 10 analysts.

**Margin**: 99%+ (process 10K credentials for ~$50, sell for $15K)

**Year 1 Targets**:
- Custom Data Projects: $15-25K each, target 12 = $180K
- Consulting: $200/hr, target $48K
- API Subscriptions: $1.5-8K/month, target 5 by EOY = $75K
- **Total Year 1**: $303K revenue, $239K net income

---

## Target Customers

**Tier 1 - EdTech**:
- Niche.com
- Guild Education (Denver!)
- InStride
- Handshake
- SchooLinks

**Tier 2 - Credential/Data Companies**:
- Credential Engine
- Credly
- Lightcast

**Tier 3 - State Workforce Boards**:
- Florida DEO
- Indiana DWD
- Michigan LEO
- Colorado

**Tier 4 - HR Tech / Corporate Education**:
- Tuition benefit providers
- Corporate L&D platforms

---

## The Moat

1. **CTDL Expertise** - Took months to learn, no one else at Peterson's could maintain it
2. **AI Infrastructure** - Not using AI as add-on, built on AI from day one
3. **Domain Knowledge** - 6 years building education data products at Peterson's
4. **Speed** - AI-native = fast iteration, low operational cost
5. **Truth Engine** - Parent system with 51.8M entities, multi-AI orchestration

---

## The Gap

**Data infrastructure**: Built and populated
**Code**: Built and tested
**Customers**: Zero

The next step isn't more building. It's **sending the 10 emails**.

---

## Related Documents

- `BUSINESS_PLAN.md` - Complete business plan with financials
- `PROSPECT_LIST.md` - 10 target companies with contacts
- `THE_LANDING.md` - Strategic reframe (Credential Bridge IS the product)
- `ARCHITECTURE.md` - Technical architecture
- `CHANGELOG.md` - Version history and migration notes

---

## Quick Commands

```bash
# Run locally
uvicorn credential_bridge.api.main:app --reload

# Run tests
pytest --cov=credential_bridge

# Check data
bq query --use_legacy_sql=false 'SELECT table_id, row_count FROM `credential-bridge.credential_bridge.__TABLES__` ORDER BY row_count DESC'
```
