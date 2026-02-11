# Master Reproduction Checklist

**The Standard** | An organism must be FULLY IMPLEMENTED before it can reproduce. No shortcuts. No partial implementations. Every element must be complete.

**Authority**: 06_LAW.md, 00_GENESIS.md, REPRODUCTION_GUIDE.md | **Status**: CANONICAL

---

## The Absolute Standard

**Reproduction is earned through COMPLETE implementation, not presence of files.**

An organism must demonstrate:
- **Zero Syntax Errors** — Every Python file must compile
- **Zero Indentation Errors** — All code properly formatted
- **All Tests Passing** — 100% of tests must pass
- **>85% Code Coverage** — Tests must cover >85% of code
- **All APIs Implemented** — Every endpoint must be functional
- **All Data Flows Complete** — Every inhale/exhale must work
- **Every Service Complete** — All 9 phases of service life implemented

```
THE REPRODUCTION GATE - ABSOLUTE REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════

PARENT ORGANISM                    REPRODUCTION GATE                    OFFSPRING
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│                 │               │                 │               │                 │
│  MUST HAVE:     │               │  ZERO TOLERANCE │               │  Receives:      │
│  ✓ 0 syntax err │──────────────▶│  VALIDATION     │──────────────▶│  ✓ Clean DNA    │
│  ✓ 0 indent err │               │                 │               │  ✓ Spark (life) │
│  ✓ 100% tests   │               │  ANY FAILURE =  │               │  ✓ Federation   │
│  ✓ >85% coverage│               │  REPRODUCTION   │               │  ✓ Governance   │
│  ✓ All APIs     │               │  DENIED         │               │                 │
│  ✓ All flows    │               │                 │               │  (Sterile by    │
│  ✓ All services │               │                 │               │   default)      │
└─────────────────┘               └─────────────────┘               └─────────────────┘

```

---

## The 16 Absolute Requirements

An organism must satisfy ALL 16 requirements with ZERO EXCEPTIONS.

### Category 1: CODE QUALITY (Is Your Code Clean?)

#### 1.1 Syntax Validation (CRITICAL - BLOCKING)
- [ ] **Zero syntax errors** — Every .py file must compile with `py_compile`
- [ ] **Zero indentation errors** — All indentation must be consistent
- [ ] **Zero import errors** — All imports must resolve
- [ ] **Zero undefined names** — No undefined variables or functions

#### 1.2 Code Standards
- [ ] **No bare except clauses** — All exceptions must be specific
- [ ] **No hardcoded secrets** — No API keys, passwords in code
- [ ] **No TODO/FIXME in critical paths** — Critical code must be complete
- [ ] **Type hints on public APIs** — All public functions typed

#### 1.3 Static Analysis
- [ ] **Passes pylint (>8.0)** — Code quality score
- [ ] **Passes mypy** — Type checking passes
- [ ] **No security vulnerabilities** — No known CVEs in dependencies

```python
# VALIDATION: Code Quality
def validate_code_quality(organism_path: Path) -> CodeQualityReport:
    """Every Python file must be syntactically correct."""
    errors = []
    
    for py_file in organism_path.rglob("*.py"):
        # Syntax check
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(SyntaxError(file=py_file, error=str(e)))
        
        # Check for bare excepts
        content = py_file.read_text()
        if re.search(r'\bexcept\s*:', content):
            errors.append(BareExceptError(file=py_file))
    
    return CodeQualityReport(errors=errors, passed=len(errors) == 0)
```

---

### Category 2: TEST COVERAGE (Is Your Code Tested?)

#### 2.1 Test Existence (CRITICAL - BLOCKING)
- [ ] **Test files exist** — `tests/` or `Primitive/tests/` directory
- [ ] **Tests for every service** — Each service has test file
- [ ] **Tests for every module** — Each module has test file
- [ ] **Integration tests exist** — End-to-end tests present

#### 2.2 Test Execution (CRITICAL - BLOCKING)
- [ ] **All tests pass** — 100% of tests must pass
- [ ] **No skipped tests** — All tests must run
- [ ] **No flaky tests** — Tests must be deterministic
- [ ] **Tests run in <5 minutes** — Performance requirement

#### 2.3 Code Coverage (CRITICAL - BLOCKING)
- [ ] **>85% line coverage** — 85% of lines executed by tests
- [ ] **>80% branch coverage** — 80% of branches tested
- [ ] **100% coverage on critical paths** — Spark, governance, vitals
- [ ] **Coverage report generated** — `coverage.xml` or `htmlcov/`

```python
# VALIDATION: Test Coverage
def validate_test_coverage(organism_path: Path) -> TestCoverageReport:
    """All tests must pass with >85% coverage."""
    
    # Run pytest with coverage
    result = subprocess.run(
        ["pytest", "--cov=Primitive", "--cov-report=json", "--cov-fail-under=85"],
        cwd=organism_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return TestCoverageReport(
            passed=False,
            tests_passed=False,
            coverage_percent=0,
            error=result.stderr
        )
    
    # Parse coverage
    coverage_data = json.loads((organism_path / "coverage.json").read_text())
    coverage_percent = coverage_data["totals"]["percent_covered"]
    
    return TestCoverageReport(
        passed=coverage_percent >= 85,
        tests_passed=True,
        coverage_percent=coverage_percent
    )
```

---

### Category 3: SERVICE COMPLETENESS (Are Services Complete?)

#### 3.1 Service Implementation (CRITICAL - BLOCKING)
- [ ] **All services inherit ServiceAPI** — Proper base class
- [ ] **All 9 phases implemented** — Conception through Singleton
- [ ] **All services pass service_validator** — Zero errors
- [ ] **All services have tests** — Test file for each service

#### 3.2 Service APIs (CRITICAL - BLOCKING)
- [ ] **All endpoints decorated** — `@endpoint()` on all public methods
- [ ] **All endpoints documented** — Description, parameters, returns
- [ ] **All endpoints tested** — Test for each endpoint
- [ ] **All endpoints return proper types** — Dict with expected keys

#### 3.3 Service Data Flows (CRITICAL - BLOCKING)
- [ ] **inhale() implemented** — Can receive data
- [ ] **exhale() implemented** — Can produce data
- [ ] **get_state() implemented** — Returns ServiceState
- [ ] **shutdown() implemented** — Graceful cleanup

```python
# VALIDATION: Service Completeness
def validate_service_completeness(organism_path: Path) -> ServiceCompletenessReport:
    """Every service must be fully implemented."""
    from Primitive.governance.service_validator import validate_service
    from Primitive.governance.service_api.base import ServiceAPIMeta
    
    errors = []
    
    # Get all registered services
    for name, service_class in ServiceAPIMeta.get_registered().items():
        report = validate_service(service_class)
        
        if not report.is_complete:
            errors.append(ServiceIncomplete(
                service=name,
                missing=report.missing_requirements,
                error_count=report.error_count
            ))
    
    return ServiceCompletenessReport(
        passed=len(errors) == 0,
        services_checked=len(ServiceAPIMeta.get_registered()),
        errors=errors
    )
```

---

### Category 4: API COMPLETENESS (Are All APIs Working?)

#### 4.1 API Implementation (CRITICAL - BLOCKING)
- [ ] **All declared endpoints exist** — No stub methods
- [ ] **All endpoints callable** — Can be invoked
- [ ] **All endpoints return valid responses** — Proper return types
- [ ] **All endpoints handle errors** — Try/except with proper responses

#### 4.2 API Documentation
- [ ] **All endpoints have descriptions** — Non-empty description
- [ ] **All parameters documented** — Type and description
- [ ] **All returns documented** — Return type specified
- [ ] **Examples provided** — At least one example per endpoint

#### 4.3 API Testing
- [ ] **All endpoints have tests** — Test coverage for each
- [ ] **Happy path tested** — Normal operation tested
- [ ] **Error paths tested** — Error handling tested
- [ ] **Edge cases tested** — Boundary conditions tested

```python
# VALIDATION: API Completeness
def validate_api_completeness(organism_path: Path) -> APICompletenessReport:
    """Every API endpoint must be fully implemented and tested."""
    errors = []
    
    for service_class in get_all_services():
        for endpoint_name, endpoint_info in service_class._endpoints.items():
            method = getattr(service_class, endpoint_name, None)
            
            # Check method exists and is callable
            if method is None or not callable(method):
                errors.append(APINotImplemented(
                    service=service_class.SERVICE_NAME,
                    endpoint=endpoint_name
                ))
                continue
            
            # Check method is not a stub
            source = inspect.getsource(method)
            if "pass" in source and source.strip().endswith("pass"):
                errors.append(APIIsStub(
                    service=service_class.SERVICE_NAME,
                    endpoint=endpoint_name
                ))
            
            # Check method has docstring
            if not method.__doc__:
                errors.append(APIMissingDocstring(
                    service=service_class.SERVICE_NAME,
                    endpoint=endpoint_name
                ))
    
    return APICompletenessReport(passed=len(errors) == 0, errors=errors)
```

---

### Category 5: DATA FLOW COMPLETENESS (Do Data Flows Work?)

#### 5.1 Respiration (CRITICAL - BLOCKING)
- [ ] **inhale() works** — Can receive and buffer data
- [ ] **exhale() works** — Can produce and output data
- [ ] **sync() works** — Can synchronize state
- [ ] **Data validation works** — Membrane filters invalid data

#### 5.2 Internal Routing
- [ ] **call_endpoint() works** — Can route to methods
- [ ] **Error propagation works** — Errors bubble up correctly
- [ ] **State updates work** — State changes are tracked
- [ ] **Metrics updated** — Operations counted

#### 5.3 External Communication
- [ ] **get_manifest() works** — Returns valid manifest
- [ ] **to_api_response() works** — Returns API-ready data
- [ ] **Registry integration works** — Service is discoverable
- [ ] **Federation works** — Can communicate with colony

```python
# VALIDATION: Data Flow Completeness
def validate_data_flows(organism_path: Path) -> DataFlowReport:
    """Every data flow must be functional."""
    errors = []
    
    for service_class in get_all_services():
        instance = service_class()
        
        # Test inhale
        try:
            result = instance.inhale({"test": "data"})
            if result is None:
                errors.append(DataFlowError(
                    service=service_class.SERVICE_NAME,
                    flow="inhale",
                    error="Returns None"
                ))
        except NotImplementedError:
            errors.append(DataFlowNotImplemented(
                service=service_class.SERVICE_NAME,
                flow="inhale"
            ))
        
        # Test exhale
        try:
            result = instance.exhale()
            if result is None:
                errors.append(DataFlowError(
                    service=service_class.SERVICE_NAME,
                    flow="exhale",
                    error="Returns None"
                ))
        except NotImplementedError:
            errors.append(DataFlowNotImplemented(
                service=service_class.SERVICE_NAME,
                flow="exhale"
            ))
        
        # Test get_state
        try:
            state = instance.get_state()
            if not isinstance(state, ServiceState):
                errors.append(DataFlowError(
                    service=service_class.SERVICE_NAME,
                    flow="get_state",
                    error="Does not return ServiceState"
                ))
        except Exception as e:
            errors.append(DataFlowError(
                service=service_class.SERVICE_NAME,
                flow="get_state",
                error=str(e)
            ))
    
    return DataFlowReport(passed=len(errors) == 0, errors=errors)
```

---

### Category 6: IDENTITY (Who Are You?)

#### 6.1 Organism Identity
- [ ] **ORGANISM_NAME** — Unique identifier
- [ ] **ORGANISM_DID** — Decentralized identifier
- [ ] **ORGANISM_VERSION** — Semantic version
- [ ] **ORGANISM_TYPE** — genesis | fertile_daughter | sterile_daughter

#### 6.2 Lineage Documentation
- [ ] **GENESIS_ANCESTOR** — Link to original genesis
- [ ] **PARENT_DID** — Parent's DID
- [ ] **GENERATION** — Generation number
- [ ] **LINEAGE_CHAIN** — Complete ancestry

---

### Category 7: VITAL ORGANS (Are You Alive?)

#### 7.1 Core Systems (CRITICAL - BLOCKING)
- [ ] **Primitive/core/** — Core utilities present and working
- [ ] **Primitive/config/** — Configuration present and working
- [ ] **Primitive/vitals/** — Vitals present and working
- [ ] **Primitive/governance/** — Governance present and working

#### 7.2 Vital Signs Operational (CRITICAL - BLOCKING)
- [ ] **Heartbeat operational** — Phi Accrual detector works
- [ ] **Pulse operational** — Health metrics collected
- [ ] **Survival operational** — Cost monitoring active
- [ ] **Proof of Life works** — Can demonstrate aliveness

---

### Category 8: GOVERNANCE (Can You Control?)

#### 8.1 Spark System (CRITICAL - BLOCKING)
- [ ] **SparkService fully implemented** — All endpoints work
- [ ] **Spark issuance works** — Can issue sparks
- [ ] **Spark validation works** — Can validate tokens
- [ ] **Heartbeat handling works** — Can process heartbeats

#### 8.2 Cost Governance (CRITICAL - BLOCKING)
- [ ] **Cost tracking works** — Tracks all operations
- [ ] **Cost enforcement works** — Can block expensive ops
- [ ] **Budget limits enforced** — Limits respected
- [ ] **Audit trail works** — All operations logged

---

### Category 9: FEDERATION (Can You Connect?)

#### 9.1 Federation Infrastructure
- [ ] **Federation module works** — Can communicate
- [ ] **Heartbeat protocol works** — Can send heartbeats
- [ ] **Learning sharing works** — Can share learnings
- [ ] **Registry integration works** — Services discoverable

---

### Category 10: REPRODUCTION MACHINERY (Can You Birth?)

#### 10.1 Seed Infrastructure (CRITICAL - BLOCKING)
- [ ] **seed_project.py works** — Can seed projects
- [ ] **Templates valid** — All templates pass validation
- [ ] **Sterility enforcement works** — Can enforce sterility
- [ ] **Federation setup works** — Offspring get federation

---

### Category 11: DOCUMENTATION (Is It Documented?)

#### 11.1 Code Documentation
- [ ] **All public functions have docstrings** — 100% documented
- [ ] **All classes have docstrings** — 100% documented
- [ ] **All modules have docstrings** — 100% documented
- [ ] **README files present** — Each package has README

#### 11.2 API Documentation
- [ ] **All endpoints documented** — Description, params, returns
- [ ] **Examples provided** — Usage examples
- [ ] **Error codes documented** — What errors can occur
- [ ] **Changelog maintained** — Version history

---

### Category 12: SECURITY (Are You Secure?)

#### 12.1 Cryptographic Infrastructure (CRITICAL - BLOCKING)
- [ ] **Crypto module works** — Can sign/verify
- [ ] **Key generation works** — Can generate keys
- [ ] **JWT signing works** — Can create tokens
- [ ] **FIDO2 works** — Human auth ready

---

### Category 13: FOUR PILLARS (Do You Follow The Law?)

#### 13.1 Fail-Safe (CRITICAL - BLOCKING)
- [ ] **No bare excepts** — All exceptions specific
- [ ] **All errors logged** — No silent failures
- [ ] **Graceful degradation** — Can operate degraded
- [ ] **Recovery mechanisms** — Can recover

#### 13.2 No Magic
- [ ] **No hardcoded values** — All configurable
- [ ] **Explicit configuration** — All settings documented
- [ ] **Clear contracts** — All interfaces documented

#### 13.3 Observability
- [ ] **Structured logging** — All operations logged
- [ ] **Metrics collection** — Key metrics tracked
- [ ] **Audit trail** — All actions auditable

#### 13.4 Idempotency
- [ ] **Safe to retry** — Operations idempotent
- [ ] **Deterministic** — Same input = same output

---

### Category 14: TEMPLATES (Are Templates Ready?)

#### 14.1 Template Validation (CRITICAL - BLOCKING)
- [ ] **All templates have zero syntax errors** — Clean code
- [ ] **All templates pass validation** — Service validator passes
- [ ] **All templates have tests** — Tests included
- [ ] **All templates documented** — README present

---

### Category 15: OPERATIONAL READINESS (Are You Ready?)

#### 15.1 Testing (CRITICAL - BLOCKING)
- [ ] **All tests pass** — 100% pass rate
- [ ] **>85% coverage** — Coverage requirement met
- [ ] **Integration tests pass** — E2E tests work
- [ ] **Performance tests pass** — Within limits

#### 15.2 Deployment
- [ ] **Deployment scripts work** — Can deploy
- [ ] **Rollback works** — Can rollback
- [ ] **Health checks work** — Can verify health

---

### Category 16: ADVANCED PYTHON PATTERNS (Is Your Code Modern?)

**Framework Alignment**: These patterns directly support the Four Pillars (06_LAW.md)

#### 16.1 Type Safety (CRITICAL - BLOCKING)
- [ ] **No Dict[str, Any] in public APIs** — Use TypedDict for explicit contracts (No Magic)
- [ ] **All public functions typed** — Full type hints on all public functions
- [ ] **Protocols used for interfaces** — Structural typing for dependency injection
- [ ] **mypy --strict passes** — Zero type errors in codebase

#### 16.2 Memory Efficiency (CRITICAL - BLOCKING)
- [ ] **All dataclasses use slots=True** — ~40% memory reduction, predictable layout (Observability)
- [ ] **Generator expressions used** — No unnecessary list allocations
- [ ] **WeakRef for caches** — No memory leaks in service caching (Fail-Safe)
- [ ] **cached_property for expensive computations** — Lazy evaluation with caching

#### 16.3 Code Organization (CRITICAL - BLOCKING)
- [ ] **__all__ declared in all modules** — Explicit public API definition (No Magic)
- [ ] **Pattern matching for Result types** — Explicit control flow (No Magic)
- [ ] **Context managers for resources** — Guaranteed cleanup (Fail-Safe)
- [ ] **kw_only=True on dataclasses** — Prevent positional argument errors

```python
# VALIDATION: Advanced Python Patterns
def validate_advanced_patterns(organism_path: Path) -> PatternComplianceReport:
    """Every Python file must use advanced patterns."""
    violations = []
    
    for py_file in organism_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        content = py_file.read_text(encoding="utf-8")
        rel_path = py_file.relative_to(organism_path)
        
        # Check 1: No Dict[str, Any] in function signatures
        if re.search(r'def\s+\w+\([^)]*Dict\[str,\s*Any\]', content):
            violations.append(PatternViolation(
                file=rel_path,
                pattern="TypedDict",
                message="Dict[str, Any] in function signature - use TypedDict"
            ))
        
        # Check 2: Dataclasses must use slots
        if re.search(r'@dataclass\s*\n', content):
            if not re.search(r'@dataclass\(.*slots\s*=\s*True', content):
                violations.append(PatternViolation(
                    file=rel_path,
                    pattern="slots",
                    message="Dataclass without slots=True"
                ))
        
        # Check 3: Modules must have __all__
        if py_file.name != "__init__.py" and "def " in content:
            if "__all__" not in content:
                violations.append(PatternViolation(
                    file=rel_path,
                    pattern="__all__",
                    message="Module missing __all__ declaration"
                ))
    
    return PatternComplianceReport(
        passed=len(violations) == 0,
        violations=violations,
        files_checked=len(list(organism_path.rglob("*.py")))
    )
```

---

## The Reproduction Gate - Absolute Standard

### Gate Levels

| Level | Requirements | Result |
|-------|-------------|--------|
| **BLOCKED** | ANY critical failure | Cannot reproduce |
| **APPROVED** | ALL requirements pass | Can reproduce |

**There is no CONDITIONAL level.** Either the organism is fully complete, or it cannot reproduce.

### Critical Failures (ANY = BLOCKED)

These are ABSOLUTE BLOCKERS:

1. **Any syntax error** — Code must compile
2. **Any test failure** — All tests must pass
3. **Coverage < 85%** — Must have adequate coverage
4. **Any service incomplete** — All services must pass validator
5. **Any API not implemented** — All endpoints must work
6. **Any data flow broken** — All flows must function
7. **SparkService not working** — Life grants required
8. **Any bare except** — No silent failures
9. **Dict[str, Any] in public APIs** — Must use TypedDict
10. **Dataclass without slots=True** — Must use slots for memory efficiency
11. **Module without __all__** — Must declare public API
12. **mypy --strict failures** — Must pass strict type checking

### Validation Process

```python
def validate_for_reproduction(organism_path: Path) -> ReproductionValidationReport:
    """Validate an organism for reproduction - ABSOLUTE STANDARD."""
    
    report = ReproductionValidationReport()
    
    # CRITICAL CHECKS - Any failure = BLOCKED
    report.code_quality = validate_code_quality(organism_path)
    if not report.code_quality.passed:
        report.gate_level = GateLevel.BLOCKED
        report.blocking_reason = "Code quality check failed"
        return report
    
    report.test_coverage = validate_test_coverage(organism_path)
    if not report.test_coverage.passed:
        report.gate_level = GateLevel.BLOCKED
        report.blocking_reason = f"Test coverage: {report.test_coverage.coverage_percent}% (need 85%)"
        return report
    
    report.service_completeness = validate_service_completeness(organism_path)
    if not report.service_completeness.passed:
        report.gate_level = GateLevel.BLOCKED
        report.blocking_reason = "Services incomplete"
        return report
    
    report.api_completeness = validate_api_completeness(organism_path)
    if not report.api_completeness.passed:
        report.gate_level = GateLevel.BLOCKED
        report.blocking_reason = "APIs incomplete"
        return report
    
    report.data_flows = validate_data_flows(organism_path)
    if not report.data_flows.passed:
        report.gate_level = GateLevel.BLOCKED
        report.blocking_reason = "Data flows broken"
        return report
    
    # All checks passed
    report.gate_level = GateLevel.APPROVED
    return report
```

---

## Summary

**The organism must be FULLY IMPLEMENTED to reproduce.**

| Requirement | Standard | Blocking? |
|-------------|----------|-----------|
| Syntax Errors | 0 | YES |
| Indentation Errors | 0 | YES |
| Test Pass Rate | 100% | YES |
| Code Coverage | >85% | YES |
| Service Completeness | 100% | YES |
| API Implementation | 100% | YES |
| Data Flows | 100% | YES |
| Bare Excepts | 0 | YES |
| Dict[str, Any] in APIs | 0 | YES |
| Dataclasses without slots | 0 | YES |
| Modules without __all__ | 0 | YES |
| mypy --strict errors | 0 | YES |

**No shortcuts. No partial implementations. Every element must be complete.**

---

## Related Standards

- [SERVICE_COMPLETENESS_CHECKLIST.md](SERVICE_COMPLETENESS_CHECKLIST.md) — Service requirements
- [06_LAW.md](../06_LAW.md) — The Four Pillars

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial standard | Claude |
| 2026-01-21 | Upgraded to absolute standard - full implementation required | Claude |
| 2026-01-21 | Added Category 16: Advanced Python Patterns - TypedDict, slots, __all__, mypy | Claude |
