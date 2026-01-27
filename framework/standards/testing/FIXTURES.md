# Test Fixtures

**Reusable test setup with pytest fixtures.**

---

## Fixture Basics

```python
import pytest

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="user_123",
        email="test@example.com",
        name="Test User",
    )

def test_user_greeting(sample_user):
    assert sample_user.greeting() == "Hello, Test User!"
```

---

## Fixture Scopes

| Scope | Lifetime | Use Case |
|-------|----------|----------|
| `function` | Each test | Default, most common |
| `class` | Test class | Shared setup within class |
| `module` | Test file | Expensive setup (DB schema) |
| `session` | Full run | Very expensive (Docker containers) |

```python
@pytest.fixture(scope="module")
def database_schema():
    """Create schema once per module."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
```

---

## Mocking with unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def mock_api_client():
    """Mock API client for testing."""
    client = Mock(spec=ApiClient)
    client.fetch.return_value = {"status": "success"}
    return client

def test_service_uses_api_client(mock_api_client):
    service = DataService(mock_api_client)
    result = service.process()
    mock_api_client.fetch.assert_called_once()
```

---

## Patching External Dependencies

```python
@patch("module.external_api.fetch")
def test_handler_calls_external_api(mock_fetch):
    mock_fetch.return_value = {"data": "test"}
    result = handler.process()
    assert result.data == "test"
    mock_fetch.assert_called_once()
```

---

## Factory Fixtures

```python
@pytest.fixture
def create_user():
    """Factory fixture for creating users with custom attributes."""
    def _create_user(
        email: str = "test@example.com",
        name: str = "Test User",
        **kwargs,
    ) -> User:
        return User(email=email, name=name, **kwargs)
    return _create_user

def test_user_with_custom_email(create_user):
    user = create_user(email="custom@example.com")
    assert user.email == "custom@example.com"
```

---

## Temporary Files

```python
def test_file_processor(tmp_path):
    """Use pytest's tmp_path for file tests."""
    # Create test file
    test_file = tmp_path / "data.json"
    test_file.write_text('{"key": "value"}')

    # Process
    result = process_file(test_file)

    # Assert
    assert result.key == "value"
```

---

## Fixture Composition

```python
@pytest.fixture
def db_session():
    """Database session fixture."""
    ...

@pytest.fixture
def user_repository(db_session):
    """Repository fixture using db_session."""
    return UserRepository(db_session)

@pytest.fixture
def user_service(user_repository):
    """Service fixture using repository."""
    return UserService(user_repository)
```

---

## UP

[testing/INDEX.md](INDEX.md)
