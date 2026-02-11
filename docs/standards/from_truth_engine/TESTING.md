# Testing

**The Standard** | Every behavior is verified, every edge case anticipated, every regression prevented.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Coverage | Minimum 80% line coverage, 100% for critical paths |
| Structure | Arrange-Act-Assert pattern |
| Naming | `test_<function>_<scenario>_<expected>` |
| Isolation | Tests must not depend on each other |
| Speed | Unit tests < 100ms, Integration < 5s |
| Determinism | No flaky tests; same input = same output |

---

## WHY (Theory)

### The Hardening Imperative

Tests are not about proving code works. Tests are about **hardening** code against future change. Every test is a specification. Every passing test is a guarantee. Every failing test is a gift—a bug caught before production.

### The Cost Equation

| Without Tests | With Tests |
|---------------|------------|
| Bugs found in production | Bugs found in development |
| Debugging time: hours | Debugging time: minutes |
| Confidence in refactoring: zero | Confidence in refactoring: high |
| Regression frequency: constant | Regression frequency: rare |

The investment in tests pays compound interest.

---

## WHAT (Specification)

### Test Pyramid

```
          ╱╲
         ╱  ╲          E2E Tests (few, slow, broad)
        ╱────╲
       ╱      ╲        Integration Tests (some, medium)
      ╱────────╲
     ╱          ╲      Unit Tests (many, fast, focused)
    ╱────────────╲
```

| Layer | Quantity | Speed | Scope |
|-------|----------|-------|-------|
| Unit | Many (70%) | < 100ms | Single function/class |
| Integration | Some (20%) | < 5s | Component boundaries |
| E2E | Few (10%) | < 30s | Full user flows |

### MUST (Required)

1. **Test Every Public Interface** — All public functions, methods, and classes MUST have tests.

```python
# ✅ Correct - public function has tests
def calculate_total(items: list[Item]) -> Decimal:
    """Calculate order total with tax."""
    ...

def test_calculate_total_empty_list_returns_zero():
    assert calculate_total([]) == Decimal("0")

def test_calculate_total_single_item_includes_tax():
    item = Item(price=Decimal("100"), tax_rate=Decimal("0.1"))
    assert calculate_total([item]) == Decimal("110")

def test_calculate_total_multiple_items_sums_correctly():
    items = [Item(price=Decimal("50")), Item(price=Decimal("30"))]
    assert calculate_total(items) == Decimal("80")
```

2. **Arrange-Act-Assert Pattern** — All tests MUST follow AAA structure.

```python
def test_user_registration_creates_account():
    # Arrange
    user_data = {"email": "test@example.com", "password": "secure123"}
    service = UserService(mock_db)

    # Act
    result = service.register(user_data)

    # Assert
    assert result.success is True
    assert result.user.email == "test@example.com"
    mock_db.save.assert_called_once()
```

3. **Descriptive Test Names** — Names MUST describe function, scenario, and expectation.

```python
# ✅ Correct
def test_parse_date_invalid_format_raises_ValueError():
    ...

def test_calculate_discount_premium_member_gets_20_percent():
    ...

# ❌ Wrong
def test_parse_date():
    ...

def test_discount():
    ...
```

4. **Test Isolation** — Tests MUST NOT depend on execution order or shared state.

```python
# ✅ Correct - each test sets up its own state
@pytest.fixture
def clean_database():
    db = create_test_database()
    yield db
    db.cleanup()

def test_create_user(clean_database):
    ...

def test_delete_user(clean_database):
    ...

# ❌ Wrong - tests depend on each other
class TestUserFlow:
    user_id = None  # Shared state!

    def test_create_user(self):
        self.user_id = create_user()  # Other tests depend on this

    def test_update_user(self):
        update_user(self.user_id)  # Fails if test_create_user didn't run
```

5. **Critical Path 100% Coverage** — Payment, authentication, data mutation MUST have 100% coverage.

```python
# Critical paths requiring exhaustive testing:
# - Authentication flows
# - Payment processing
# - Data deletion
# - Permission checks
# - API key validation
```

6. **No Flaky Tests** — Tests MUST be deterministic. If a test fails intermittently, fix or delete it.

```python
# ❌ Flaky - depends on timing
def test_cache_expires():
    cache.set("key", "value", ttl=1)
    time.sleep(1.1)  # Race condition!
    assert cache.get("key") is None

# ✅ Deterministic - mock time
def test_cache_expires(mock_time):
    cache.set("key", "value", ttl=1)
    mock_time.advance(2)
    assert cache.get("key") is None
```

### SHOULD (Recommended)

1. **Property-Based Testing** — Use hypothesis for edge case discovery.

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(items):
    sorted_once = sorted(items)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice
```

2. **Mutation Testing** — Verify tests catch code changes.

3. **Test Documentation** — Complex test scenarios SHOULD have docstrings explaining intent.

4. **Parameterized Tests** — Use parametrize for testing multiple inputs.

```python
@pytest.mark.parametrize("input,expected", [
    ("", False),
    ("a", False),
    ("abc@", False),
    ("abc@def", False),
    ("abc@def.com", True),
])
def test_is_valid_email(input, expected):
    assert is_valid_email(input) == expected
```

### MAY (Optional)

1. **Snapshot Testing** — For complex output verification.
2. **Contract Testing** — For API boundary verification.
3. **Chaos Testing** — For resilience verification.

### MUST NOT (Prohibited)

1. **Never Test Implementation** — Test behavior, not internal structure.
2. **Never Skip Without Reason** — `@pytest.skip` requires documented justification.
3. **Never Catch All Exceptions** — Let unexpected exceptions fail the test.
4. **Never Use Production Data** — Tests use synthetic or anonymized data only.

---

## HOW (Reference)

### Test File Structure

```
project/
├── src/
│   └── module/
│       ├── __init__.py
│       └── service.py
└── tests/
    ├── conftest.py           # Shared fixtures
    ├── unit/
    │   └── test_service.py   # Unit tests mirror src structure
    ├── integration/
    │   └── test_api.py       # Integration tests by feature
    └── e2e/
        └── test_flows.py     # End-to-end user flows
```

### Fixture Patterns

```python
# conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_database():
    """Provide a mock database for unit tests."""
    db = MagicMock()
    db.query.return_value = []
    return db

@pytest.fixture
def test_user():
    """Provide a standard test user."""
    return User(
        id="test-user-123",
        email="test@example.com",
        role="standard"
    )

@pytest.fixture(scope="module")
def database_connection():
    """Provide real database for integration tests."""
    conn = create_test_database()
    yield conn
    conn.close()
    cleanup_test_database()
```

### Test Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--tb=short",
    "-ra",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 80
```

### Mocking Best Practices

```python
# Mock at the boundary, not deep in implementation
from unittest.mock import patch, MagicMock

# ✅ Correct - mock external dependency
def test_fetch_user_handles_api_error():
    with patch('module.external_api.get') as mock_get:
        mock_get.side_effect = APIError("Connection failed")

        result = fetch_user("123")

        assert result.success is False
        assert "Connection failed" in result.error

# ❌ Wrong - mocking internal implementation
def test_fetch_user_calls_internal_method():
    with patch.object(UserService, '_internal_method') as mock:
        ...  # Testing implementation, not behavior
```

---

### Typed Fixtures (PEP 484 Compliant)

Per [CODE_QUALITY.md](CODE_QUALITY.md), fixtures should have type hints:

```python
# conftest.py
from typing import Generator
import pytest
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TestUser:
    """Typed test user for fixtures."""
    id: str
    email: str
    role: str

@pytest.fixture
def test_user() -> TestUser:
    """Provide a typed test user."""
    return TestUser(
        id="test-user-123",
        email="test@example.com",
        role="standard",
    )

@pytest.fixture
def temp_jsonl_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary JSONL file for testing."""
    file_path = tmp_path / "test_data.jsonl"
    yield file_path
    if file_path.exists():
        file_path.unlink()

@pytest.fixture
def mock_dlq(tmp_path: Path) -> "DeadLetterQueue":
    """Provide a DLQ instance for testing."""
    from src.error_handling import DeadLetterQueue
    return DeadLetterQueue(tmp_path, "test_pipeline")
```

---

### Pipeline Testing Patterns

#### Testing HOLD → AGENT → HOLD

```python
from typing import Dict, Any, List
import pytest
from pathlib import Path
import json

class TestPipelinePattern:
    """Test the universal pipeline pattern."""

    @pytest.fixture
    def input_hold(self, tmp_path: Path) -> Path:
        """Create HOLD₁ with test data."""
        hold_path = tmp_path / "input.jsonl"
        records = [
            {"id": "1", "content": "test content 1"},
            {"id": "2", "content": "test content 2"},
        ]
        with open(hold_path, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        return hold_path

    @pytest.fixture
    def output_hold(self, tmp_path: Path) -> Path:
        """Create HOLD₂ path."""
        return tmp_path / "output.jsonl"

    def test_pipeline_transforms_all_records(
        self,
        input_hold: Path,
        output_hold: Path,
    ) -> None:
        """Pipeline should process all input records to output."""
        # Arrange
        from src.pipeline import run_stage

        # Act
        result = run_stage(input_hold, output_hold)

        # Assert
        assert result.success_count == 2
        assert result.failure_count == 0
        assert output_hold.exists()

        with open(output_hold) as f:
            output_records = [json.loads(line) for line in f]
        assert len(output_records) == 2

    def test_pipeline_isolates_failures(
        self,
        input_hold: Path,
        output_hold: Path,
        mock_dlq: "DeadLetterQueue",
    ) -> None:
        """One record failure should not kill the batch."""
        # Add a record that will fail
        with open(input_hold, "a") as f:
            f.write(json.dumps({"id": "bad", "content": None}) + "\n")

        result = run_stage(input_hold, output_hold, dlq=mock_dlq)

        assert result.success_count == 2
        assert result.failure_count == 1
        assert mock_dlq.count() == 1
```

#### Testing DLQ Behavior

```python
def test_dlq_captures_failed_records(
    mock_dlq: "DeadLetterQueue",
) -> None:
    """DLQ should capture all failed records with context."""
    # Arrange
    record = {"id": "123", "content": "test"}
    error = ValueError("Invalid content")

    # Act
    mock_dlq.send(record, error, stage="entity_creation")

    # Assert
    assert mock_dlq.count() == 1

def test_dlq_replay_reprocesses_records(
    mock_dlq: "DeadLetterQueue",
) -> None:
    """DLQ replay should attempt to reprocess failed records."""
    # Arrange
    record = {"id": "123", "content": "test"}
    mock_dlq.send(record, ValueError("temp error"), stage="test")

    successful_processor = lambda r: None  # Now succeeds

    # Act
    success, failure = mock_dlq.replay(successful_processor)

    # Assert
    assert success == 1
    assert failure == 0
    assert mock_dlq.count() == 0  # DLQ cleared
```

#### Testing Batch Processing

```python
@pytest.mark.parametrize("batch_size,expected_batches", [
    (1000, 1),
    (500, 2),
    (100, 10),
])
def test_batch_processing_respects_size(
    input_hold: Path,
    batch_size: int,
    expected_batches: int,
) -> None:
    """Batch processor should create correct number of batches."""
    # Create 1000 records
    with open(input_hold, "w") as f:
        for i in range(1000):
            f.write(json.dumps({"id": str(i)}) + "\n")

    batches_processed = []

    def track_batch(batch: List[Dict]) -> None:
        batches_processed.append(len(batch))

    process_in_batches(input_hold, batch_size, track_batch)

    assert len(batches_processed) == expected_batches
```

---

### Testing Async Code

```python
import pytest
import asyncio
from typing import List

@pytest.mark.asyncio
async def test_async_batch_processing() -> None:
    """Async batch processor should handle concurrent operations."""
    results: List[str] = []

    async def async_processor(record: dict) -> str:
        await asyncio.sleep(0.01)  # Simulate async work
        return f"processed_{record['id']}"

    records = [{"id": str(i)} for i in range(10)]

    # Process concurrently
    tasks = [async_processor(r) for r in records]
    results = await asyncio.gather(*tasks)

    assert len(results) == 10
    assert all(r.startswith("processed_") for r in results)
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| pytest | All tests pass | error |
| coverage | Minimum 80% | error |
| coverage | Critical paths 100% | error |
| pytest-randomly | No order dependence | warning |

### CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests and Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      # Code Quality (from CODE_QUALITY.md)
      - name: Type check (mypy)
        run: mypy src/ --strict

      - name: Lint (ruff)
        run: ruff check src/

      - name: Format check (ruff)
        run: ruff format --check src/

  test:
    runs-on: ubuntu-latest
    needs: quality  # Only run tests if quality passes
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      # Unit Tests
      - name: Run unit tests
        run: |
          pytest tests/unit -v \
            --cov=src \
            --cov-fail-under=80 \
            --cov-report=xml \
            -x  # Stop on first failure

      # Integration Tests (only on main branch)
      - name: Run integration tests
        if: github.ref == 'refs/heads/main'
        run: pytest tests/integration -v -m integration

      # Upload coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

### Escape Hatch

For tests that must be temporarily skipped:

```python
@pytest.mark.skip(reason="standard:override testing-coverage - Blocked by #456, tracking in #457")
def test_feature_not_yet_implemented():
    ...
```

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Testing error scenarios and DLQ behavior |
| [DEPRECATION.md](DEPRECATION.md) | Testing deprecated code paths |
| [CODE_QUALITY.md](CODE_QUALITY.md) | Typed fixtures, test function signatures |
| [PIPELINE_STANDARD.md](PIPELINE_STANDARD.md) | Pipeline-specific testing requirements |
| [LOGGING.md](LOGGING.md) | Testing log output |

---

## Industry Alignment

This standard incorporates best practices from:
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [Hypothesis](https://hypothesis.readthedocs.io/) - Property-based testing
- [Real Python: Testing](https://realpython.com/python-testing/) - Comprehensive guides
- [Google Testing Blog](https://testing.googleblog.com/) - Testing philosophy

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-25 | Added typed fixtures, pipeline testing, async patterns, CI/CD integration | Claude |
| 2025-01-18 | Initial standard | Claude |
