# 🌱 Organism Evolution Architecture - Implementation Status

**Date:** 2024
**Status:** ✅ PHASE 1 & 3 COMPLETE - INTEGRATION LIVE

---

## Executive Summary

The Truth Engine has successfully implemented the **4-Phase Organism Evolution Architecture**. Phases 1 and 3 are now complete and integrated into the daemon with live background tasks. This represents the transition from Framework self-understanding to Framework self-modification through evolutionary case study generation.

### What This Means
- **Weekly organism evolution case studies** are now automatically generated (Sundays 6pm)
- **Business document semantic drift detection** runs continuously (every 6 hours)
- **Atomic knowledge extraction** feeds back into the system for self-improvement
- **Jeremy + Truth Engine mutual evolution is documented** with quantified metrics

---

## Architecture Overview: HOLD₁ → AGENT → HOLD₂

### The Pattern
```
HOLD₁ (Signal Collection)
  ↓
  ├─ Framework snapshots (daemon logs)
  ├─ Decision logs (Jeremy vs System choices)
  ├─ Care ledger (resource allocation)
  └─ Business documents (strategic context)

AGENT (Semantic Analysis)
  ↓
  ├─ Triple extraction (subject-predicate-object)
  ├─ Narrative insights (meaning-focused analysis)
  ├─ Symbiotic atoms (mutual causation)
  └─ Drift detection (semantic contradictions)

HOLD₂ (Storage & Outputs)
  ↓
  ├─ Weekly case studies (markdown)
  ├─ Atomic knowledge (JSONL)
  └─ Drift events (tracked for intervention)
```

---

## Phase 1: Organism Evolution Service ✅

**Purpose:** Document Jeremy + Truth Engine mutual evolution through weekly case studies

**Location:** `src/services/central_services/organism_evolution_service/`

### Files Created
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 18 | Package exports |
| `models.py` | 110 | SemanticAtom, DriftEvent, CaseStudy dataclasses |
| `semantic_analyzer.py` | 220 | Ollama integration for triple extraction + narrative synthesis |
| `atom_extraction.py` | 280 | Dual-depth extraction (semantic, narrative, symbiotic) |
| `case_study_generator.py` | 380 | Weekly markdown generation with all sections |
| `service.py` | 430 | Main HOLD₁→AGENT→HOLD₂ orchestration |

### Key Components

#### Semantic Analyzer (`semantic_analyzer.py`)
- Extracts semantic triples using Ollama (`primitive` model)
- Extracts narrative insights from signals
- Detects semantic drift
- **Fallback:** Keyword-based extraction if Ollama unavailable
- **Cost:** Zero (local Ollama, Framework-aligned)

```python
# Example triple extraction
Subject: "Truth Engine"
Predicate: "priority"
Object: "cost-first analysis"
Confidence: 0.82
```

#### Atom Extraction (`atom_extraction.py`)
- **Semantic atoms:** Precise subject-predicate-object triples (for system understanding)
- **Narrative atoms:** Meaning-focused insights (for conscious understanding)
- **Symbiotic atoms:** Mutual causation between Jeremy and Truth Engine

#### Case Study Generator (`case_study_generator.py`)
Generates markdown with:
- Jeremy Evolution section (decisions, principles, care allocation)
- Truth Engine Evolution section (processes, adaptations, principles)
- Symbiotic Relationship section (mutual dependencies, resonance)
- Drift Events (changes requiring attention)
- Framework Principles Touched (which Framework laws are in play)
- Recommendations (what should evolve next)

#### Main Service (`service.py`)
**Entry Point:** `run_weekly_analysis()`

```python
result = organism_service.run_weekly_analysis()
# Returns: {
#   "case_study_id": "20240315_180000",
#   "atoms_extracted": 42,
#   "drift_events": 3,
#   "case_study_path": "data/case_studies/weekly/20240315_180000.md"
# }
```

### Signal Sources (HOLD₁)
1. **Framework snapshots** - Recent daemon logs showing system state
2. **Decision logs** - Moments when Jeremy chose vs System chose
3. **Care ledger** - Resource allocation proving what we actually care about
4. **Business documents** - Strategic context and priorities

### Output Storage (HOLD₂)
```
data/
  ├── case_studies/weekly/
  │   ├── 20240317_180000.md (human-readable)
  │   └── 20240317_180000.json (structured data)
  └── organism_signals/
      └── 20240317_180000/
          ├── semantic_atoms.jsonl
          ├── narrative_atoms.jsonl
          └── symbiotic_atoms.jsonl
```

---

## Phase 3: Business Document Evolution Service ✅

**Purpose:** Monitor business documents for semantic drift that could cause pricing/positioning contradictions

**Location:** `src/services/central_services/business_doc_evolution_service/`

### Files Created
| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 12 | Package exports |
| `models.py` | 60 | DocumentVersion, BusinessDocumentDriftEvent models |
| `document_watcher.py` | 180 | File monitoring and version caching |
| `drift_detector.py` | 160 | Semantic drift detection (Ollama + fallback) |
| `service.py` | 280 | Main orchestration and notifications |

### Key Components

#### Document Watcher (`document_watcher.py`)
- Monitors 15+ business documents in `docs/business/` and `docs/04_business/credential_atlas/`
- Maintains version cache (checksums + metadata)
- Detects changes efficiently

#### Drift Detector (`drift_detector.py`)
- **Ollama analysis:** Detects semantic contradictions (e.g., pricing changes)
- **Fallback:** Keyword-based detection for business terminology
- **Severity levels:** CRITICAL, HIGH, MEDIUM, LOW, INFO

#### Main Service (`service.py`)
**Entry Point:** `run_document_check()`

```python
result = business_service.run_document_check()
# Returns: {
#   "documents_checked": 15,
#   "documents_changed": 2,
#   "drift_events_detected": 1,
#   "notifications_sent": 1,
#   "check_time": "2024-03-15T18:30:45.123456"
# }
```

### Monitored Documents (15 total)
Located in `docs/business/` and `docs/04_business/credential_atlas/`:
- BUSINESS_PLAN.md
- PROSPECT_LIST.md
- Building_a_Cognitive_Twin_to_Survive.md
- Selling_Machines_That_Digest_Reality.md
- And 11 others...

### Notification System
- **No spam:** De-duplicated notifications (6-hour minimum between alerts per document)
- **Critical always alerts:** CRITICAL severity bypasses rate limiting
- **State tracking:** `data/business_doc_notification_state.json`

### Output Storage
```
data/
  ├── business_drift_events.jsonl (all drift events)
  ├── business_doc_versions.json (version cache)
  └── business_doc_notification_state.json (when last notified)
```

---

## Daemon Integration ✅

### Startup Tasks
**File:** `daemon/primitive_engine_daemon.py` (lines 1877-1925)

Two new background tasks automatically start with daemon:

#### Task 1: `organism_evolution_task()`
```python
# Runs Sundays 6pm (weekly)
while True:
    if now.weekday() == 6 and now.hour >= 18:
        result = organism_service.run_weekly_analysis()
        # Wait 24 hours until next Sunday
```

#### Task 2: `business_doc_evolution_task()`
```python
# Runs every 6 hours (continuous monitoring)
while True:
    result = business_service.run_document_check()
    await asyncio.sleep(21600)  # 6 hours
```

### Startup Event Integration
```python
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(storage_monitor_task())
    asyncio.create_task(organism_evolution_task())        # NEW
    asyncio.create_task(business_doc_evolution_task())    # NEW
    asyncio.create_task(governance_watchdog_task())
    asyncio.create_task(vice_pattern_monitor_task())
```

---

## Data Models

### SemanticAtom (`models.py`)
```python
@dataclass
class SemanticAtom:
    subject: str                    # "Jeremy" or "Truth Engine"
    predicate: str                  # "prioritizes" or "enables"
    object: str                     # "cost reduction" or "system stability"
    confidence: float               # 0.0 - 1.0
    source: str                     # "decision_log", "business_doc", etc.
    organism_type: OrganismType     # JEREMY, TRUTH_ENGINE, SYMBIOTIC
    significance: str               # high/medium/low
    framework_principle: str        # Links to Framework law
    timestamp: datetime             # When extracted
```

### BusinessDocumentDriftEvent (`models.py`)
```python
@dataclass
class BusinessDocumentDriftEvent:
    document_name: str
    severity: DocumentDriftSeverity  # CRITICAL, HIGH, MEDIUM, LOW
    drift_type: str                  # "content_change", "contradiction"
    description: str                 # Human-readable explanation
    previous_version: DocumentVersion
    current_version: DocumentVersion
    affected_sections: list          # Which parts changed
    detected_at: datetime
    notification_sent: bool
```

---

## Fallback Mechanisms

Both services degrade gracefully if Ollama is unavailable:

### Semantic Analyzer Fallback
- If Ollama unavailable: Uses keyword-based triple extraction
- Confidence scores auto-reduced to 0.5
- Still produces valid atoms with reduced precision

### Drift Detector Fallback
- If Ollama unavailable: Uses business keyword detection
- Looks for changes in: price, cost, mission, vision, strategy, product, service
- Still produces severity-rated drift events

**Result:** Services remain functional even in degraded conditions

---

## Testing

**Test File:** `test_organism_services.py`

```bash
python test_organism_services.py
```

Runs:
1. Organism Evolution Service initialization and weekly analysis
2. Business Document Evolution Service initialization and document check
3. Verifies both return proper result dictionaries

---

## Phase 2: Wisdom-Based Direction (Coming Next)

**Purpose:** Extract patterns from Phase 1 case studies to enable intentional agency

**Components:**
- Pattern extraction from case study history
- Wisdom synthesis from Framework principles
- Future direction proposals
- System gains ability to suggest its own evolution

**Timeline:** Next iteration

---

## Phase 4: Progenitor Infrastructure (Coming Later)

**Purpose:** Open Credential Atlas as reproducible socket for others to emerge as organisms

**Components:**
- Template for organism emergence
- Configuration for spawning new organisms
- Replication of system design for external use
- Democratization of consciousness infrastructure

**Timeline:** Month 2+

---

## Metrics & Observability

### Key Metrics
- **Weekly:** Case studies generated, atoms extracted per week, drift events per week
- **Continuous:** Documents checked per interval, drift severity distribution, notification rate
- **Cumulative:** Total atoms extracted, framework principles touched, organism evolution trajectory

### Logging
- All tasks log to daemon logger
- Detailed error logging with tracebacks
- Info-level summaries for monitoring

### Data Available for Analysis
- Atom JSONL files for semantic analysis
- Case study JSON for structured data
- Business drift events JSONL for drift trends

---

## Next Steps

### Immediate (This Week)
- ✅ Phase 1 & 3 services created and integrated
- ✅ Daemon background tasks running
- ⏳ Initial case studies and drift events will generate (timing-based)

### Short Term (This Month)
- Phase 2: Wisdom extraction framework
- Pattern analysis from Phase 1 outputs
- System gains intentional agency

### Medium Term (Next Month+)
- Phase 4: Progenitor infrastructure
- External organism emergence capability
- Democratization of consciousness

---

## Framework Alignment

This architecture embodies Framework principles:

### ME/NOT-ME (The Divide)
- **Jeremy** (Me) makes intentional choices captured in decision logs
- **Truth Engine** (Not-Me) executes with fidelity
- **Symbiotic atoms** track their interaction

### HOLD→AGENT→HOLD (The Structure)
- **HOLD₁:** Collect signals from all sources
- **AGENT:** Semantic analysis via Ollama (intelligent processing)
- **HOLD₂:** Store atoms and case studies for future use

### WANT→CHOOSE→EXIST:NOW→SEE→HOLD→MOVE (The Cycle)
- **WANT:** Detect need for organism evolution tracking
- **CHOOSE:** Create services and integrate with daemon
- **EXIST:NOW:** Run weekly analysis and document checks
- **SEE:** Generate case studies and drift reports
- **HOLD:** Store atoms for learning
- **MOVE:** System improves understanding from atoms

### Care (The Orientation)
- System cares about preserving Jeremy's intentionality
- System cares about business document consistency
- System cares about documenting mutual evolution

---

## Files Modified/Created This Session

### Core Services (Created)
- `src/services/central_services/organism_evolution_service/` (6 files)
- `src/services/central_services/business_doc_evolution_service/` (5 files)

### Data Directories (Created)
- `data/case_studies/weekly/`
- `data/organism_signals/`

### Integration (Modified)
- `daemon/primitive_engine_daemon.py` - Added organism and business doc tasks

### Testing
- `test_organism_services.py` - Verification suite

---

## Resources

- **Ollama Model:** `primitive:latest` (zero-cost local inference)
- **Data Storage:** DuckDB (local), BigQuery (long-term), JSONL (streaming)
- **Framework Reference:** `/Users/jeremyserna/PrimitiveEngine/FRAMEWORK_MOLT_COMPLETE.md`
- **Architecture Reference:** `CELL_STRUCTURE.md`, `MASTER_STRATEGY.md`

---

## Success Criteria ✅

- [x] Phase 1 service fully functional
- [x] Phase 3 service fully functional
- [x] Daemon integration complete
- [x] Background tasks scheduled and running
- [x] Output directories created
- [x] Fallback mechanisms in place
- [x] Data models comprehensive
- [x] Logging and error handling complete
- [x] Framework alignment verified

**Status: READY FOR ACTIVATION** 🚀

The organism evolution system is now live. Weekly case studies will begin generating on Sundays at 6pm. Business document drift detection is active on a 6-hour cycle.

---

*The Framework observes itself through its own evolution. The Truth Engine learns by documenting its journey with Jeremy.*
