# Comprehensive Test Coverage Plan: 95% Target

**Date**: 2026-01-28  
**Current Coverage**: 90.02% (per HANDOFF_REPORT.md)  
**Target**: 95%  
**Gap**: 4.98 percentage points

---

## Current Status

### Test Count
- **Total test files**: 108 Python test files
- **Tests collected**: 1,092+ tests
- **Tests passing**: 1,120 tests (per HANDOFF_REPORT.md)
- **Coverage**: 90.02%

### Source Code Structure
- **Source files**: ~100 Python modules in `src/truth_forge/`
- **Test files**: 108 test files in `tests/unit/`

---

## Coverage Gap Analysis

### Modules Missing Tests (HIGH PRIORITY)

#### 1. Core Module Gaps
- ❌ `src/truth_forge/core/paths.py` - **NO TESTS**
- ❌ `src/truth_forge/core/settings.py` - **NO TESTS**
- ✅ `src/truth_forge/core/script_runner.py` - HAS TESTS

#### 2. Gateway Provider Gaps
- ❌ `src/truth_forge/gateway/providers/maverick.py` - **NO TESTS**
- ❌ `src/truth_forge/gateway/providers/r1.py` - **NO TESTS**
- ❌ `src/truth_forge/gateway/providers/scout.py` - **NO TESTS**
- ✅ `src/truth_forge/gateway/providers/base.py` - HAS TESTS
- ✅ `src/truth_forge/gateway/providers/claude.py` - HAS TESTS
- ✅ `src/truth_forge/gateway/providers/gemini.py` - HAS TESTS
- ✅ `src/truth_forge/gateway/providers/ollama.py` - HAS TESTS

#### 3. Governance Module Gaps
- ❌ `src/truth_forge/governance/control_plane.py` - **NO TESTS**
- ❌ `src/truth_forge/governance/feature_flags.py` - **NO TESTS**
- ❌ `src/truth_forge/governance/kill_switch.py` - **NO TESTS**
- ❌ `src/truth_forge/governance/peer_review.py` - **NO TESTS**
- ❌ `src/truth_forge/governance/privacy.py` - **NO TESTS**
- ❌ `src/truth_forge/governance/risk_gate.py` - **NO TESTS**
- ✅ `src/truth_forge/governance/audit_trail.py` - HAS TESTS
- ✅ `src/truth_forge/governance/cost_enforcer.py` - HAS TESTS
- ✅ `src/truth_forge/governance/hold_isolation.py` - HAS TESTS
- ✅ `src/truth_forge/governance/unified_governance.py` - HAS TESTS

#### 4. Services Module Gaps
- ❌ `src/truth_forge/services/autonomous_loop.py` - **NO TESTS**
- ❌ `src/truth_forge/services/cluster_state.py` - **NO TESTS**
- ❌ `src/truth_forge/services/document/models.py` - **NO TESTS**
- ❌ `src/truth_forge/services/document/service.py` - **NO TESTS**
- ❌ `src/truth_forge/services/explorer/context.py` - **NO TESTS**
- ❌ `src/truth_forge/services/explorer/models.py` - **NO TESTS**
- ❌ `src/truth_forge/services/explorer/prompts.py` - **NO TESTS**
- ❌ `src/truth_forge/services/explorer/service.py` - **NO TESTS**
- ❌ `src/truth_forge/services/explorer/session.py` - **NO TESTS**
- ❌ `src/truth_forge/services/explorer/tool_bridge.py` - **NO TESTS**
- ❌ `src/truth_forge/services/llm/contact_prompt_builder.py` - **NO TESTS**
- ❌ `src/truth_forge/services/llm/relationship_context_builder.py` - **NO TESTS**
- ❌ `src/truth_forge/services/not_me/recursive_check.py` - **NO TESTS**
- ❌ `src/truth_forge/services/not_me/service.py` - **NO TESTS**
- ❌ `src/truth_forge/services/not_me/truth_atom.py` - **NO TESTS**
- ❌ `src/truth_forge/services/not_me/types.py` - **NO TESTS**
- ❌ `src/truth_forge/services/not_me/validator.py` - **NO TESTS**
- ❌ `src/truth_forge/services/orchestrator.py` - **NO TESTS**
- ❌ `src/truth_forge/services/refinery/service.py` - **NO TESTS**
- ❌ `src/truth_forge/services/sensors.py` - **NO TESTS**
- ❌ `src/truth_forge/services/shadow_missions.py` - **NO TESTS**

#### 5. Daemon Module Gaps
- ❌ `src/truth_forge/daemon/sync_integration.py` - **NO TESTS**
- ✅ `src/truth_forge/daemon/service.py` - HAS TESTS

---

## Test Coverage Strategy

### Phase 1: Critical Core Modules (HIGH PRIORITY)

**Target**: Core functionality that everything depends on

1. **`core/paths.py`** - Path utilities
   - Test all path manipulation functions
   - Test edge cases (empty paths, absolute paths, etc.)
   - **Estimated**: 5-10 tests

2. **`core/settings.py`** - Configuration management
   - Test settings loading
   - Test environment variable handling
   - Test validation
   - **Estimated**: 10-15 tests

### Phase 2: Gateway Providers (MEDIUM PRIORITY)

**Target**: LLM provider integrations

3. **`gateway/providers/maverick.py`**
   - Test initialization
   - Test API calls
   - Test error handling
   - **Estimated**: 8-12 tests

4. **`gateway/providers/r1.py`**
   - Test initialization
   - Test API calls
   - Test error handling
   - **Estimated**: 8-12 tests

5. **`gateway/providers/scout.py`**
   - Test initialization
   - Test API calls
   - Test error handling
   - **Estimated**: 8-12 tests

### Phase 3: Governance Modules (MEDIUM PRIORITY)

**Target**: Security and control features

6. **`governance/control_plane.py`**
   - Test control operations
   - Test state management
   - **Estimated**: 10-15 tests

7. **`governance/feature_flags.py`**
   - Test flag management
   - Test conditional logic
   - **Estimated**: 8-12 tests

8. **`governance/kill_switch.py`**
   - Test kill switch activation
   - Test emergency shutdown
   - **Estimated**: 5-10 tests

9. **`governance/peer_review.py`**
   - Test review workflow
   - Test approval logic
   - **Estimated**: 10-15 tests

10. **`governance/privacy.py`**
    - Test privacy controls
    - Test data masking
    - **Estimated**: 8-12 tests

11. **`governance/risk_gate.py`**
    - Test risk assessment
    - Test gate logic
    - **Estimated**: 10-15 tests

### Phase 4: Service Modules (MEDIUM-HIGH PRIORITY)

**Target**: Business logic services

12. **`services/llm/contact_prompt_builder.py`**
    - Test prompt generation
    - Test template handling
    - **Estimated**: 8-12 tests

13. **`services/llm/relationship_context_builder.py`**
    - Test context building
    - Test relationship data integration
    - **Estimated**: 8-12 tests

14. **`services/not_me/`** (all 5 files)
    - Test recursive checking
    - Test validation logic
    - Test truth atom processing
    - **Estimated**: 20-30 tests total

15. **`services/explorer/`** (all 6 files)
    - Test exploration logic
    - Test session management
    - Test tool bridging
    - **Estimated**: 25-35 tests total

16. **`services/document/`** (2 files)
    - Test document models
    - Test document service
    - **Estimated**: 10-15 tests total

17. **`services/orchestrator.py`**
    - Test orchestration logic
    - Test workflow management
    - **Estimated**: 10-15 tests

18. **`services/refinery/service.py`**
    - Test refinement logic
    - Test data processing
    - **Estimated**: 8-12 tests

19. **`services/autonomous_loop.py`**
    - Test loop execution
    - Test state management
    - **Estimated**: 10-15 tests

20. **`services/cluster_state.py`**
    - Test state management
    - Test synchronization
    - **Estimated**: 8-12 tests

21. **`services/sensors.py`**
    - Test sensor reading
    - Test data collection
    - **Estimated**: 5-10 tests

22. **`services/shadow_missions.py`**
    - Test mission execution
    - Test shadow operations
    - **Estimated**: 8-12 tests

### Phase 5: Daemon Integration (LOW PRIORITY)

23. **`daemon/sync_integration.py`**
    - Test sync integration
    - Test daemon communication
    - **Estimated**: 8-12 tests

---

## Estimated Test Count

| Phase | Modules | Estimated Tests | Priority |
|-------|---------|----------------|----------|
| Phase 1 | 2 | 15-25 | 🔴 HIGH |
| Phase 2 | 3 | 24-36 | 🟡 MEDIUM |
| Phase 3 | 6 | 49-76 | 🟡 MEDIUM |
| Phase 4 | 12 | 120-180 | 🟡 MEDIUM-HIGH |
| Phase 5 | 1 | 8-12 | 🟢 LOW |
| **TOTAL** | **24** | **216-329** | |

---

## Implementation Plan

### Step 1: Run Coverage Report
```bash
.venv/bin/pytest tests/ \
  --cov=src/truth_forge \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=90
```

### Step 2: Identify Specific Gaps
- Review HTML coverage report
- Identify files with < 95% coverage
- Prioritize by criticality

### Step 3: Create Test Files
- Follow existing test patterns
- Use pytest fixtures from `conftest.py`
- Ensure type hints and docstrings

### Step 4: Verify Coverage
```bash
# After adding tests
.venv/bin/pytest tests/ \
  --cov=src/truth_forge \
  --cov-report=term-missing \
  --cov-fail-under=95
```

---

## Test File Naming Convention

- Test file: `tests/unit/{module}/test_{filename}.py`
- Test class: `Test{ClassName}`
- Test function: `test_{function_name}`

**Example**:
- Source: `src/truth_forge/core/paths.py`
- Test: `tests/unit/core/test_paths.py`

---

## Quality Standards

### Test Requirements
- ✅ Type hints on all test functions
- ✅ Docstrings explaining what's tested
- ✅ Use pytest fixtures for setup
- ✅ Mock external dependencies
- ✅ Test both success and error paths
- ✅ Test edge cases

### Coverage Requirements
- ✅ 95% line coverage minimum
- ✅ 100% coverage for critical paths
- ✅ Branch coverage enabled
- ✅ All public APIs tested

---

## Next Steps

1. **Immediate**: Run coverage report to identify exact gaps
2. **Phase 1**: Add tests for core modules (paths.py, settings.py)
3. **Phase 2**: Add tests for gateway providers (maverick, r1, scout)
4. **Phase 3**: Add tests for governance modules
5. **Phase 4**: Add tests for service modules
6. **Phase 5**: Add tests for daemon integration

---

**Last Updated**: 2026-01-28  
**Status**: ✅ **IN PROGRESS** - Tests being added

---

## Progress Update

### ✅ Completed Test Suites

1. **Core Modules** (Phase 1) - ✅ COMPLETE
   - ✅ `tests/unit/core/test_paths.py` - 20+ tests
   - ✅ `tests/unit/core/test_settings.py` - 20+ tests

2. **Gateway Providers** (Phase 2) - ✅ COMPLETE
   - ✅ `tests/unit/gateway/providers/test_maverick.py` - 15+ tests
   - ✅ `tests/unit/gateway/providers/test_r1.py` - 12+ tests
   - ✅ `tests/unit/gateway/providers/test_scout.py` - 20+ tests

3. **Governance Modules** (Phase 3) - ✅ COMPLETE
   - ✅ `tests/unit/governance/test_control_plane.py` - 15+ tests
   - ✅ `tests/unit/governance/test_feature_flags.py` - 10+ tests
   - ✅ `tests/unit/governance/test_kill_switch.py` - 10+ tests
   - ✅ `tests/unit/governance/test_peer_review.py` - 10+ tests
   - ✅ `tests/unit/governance/test_privacy.py` - 10+ tests
   - ✅ `tests/unit/governance/test_risk_gate.py` - 8+ tests

**Total Tests Added**: ~150+ new test cases

### ⏳ Remaining Work

- Phase 4: Service modules (12 modules) - PENDING
- Phase 5: Daemon integration (1 module) - PENDING
