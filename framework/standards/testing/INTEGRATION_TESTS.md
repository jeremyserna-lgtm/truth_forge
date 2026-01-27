# Integration Tests

**Tests that verify component boundaries and interactions.**

---

## What Integration Tests Cover

| Boundary | Tests |
|----------|-------|
| Database | Queries, transactions, migrations |
| APIs | HTTP requests, response parsing |
| File I/O | Reading, writing, permissions |
| Services | Component interactions |

---

## Database Integration

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_repository_saves_and_retrieves(db_session):
    # Arrange
    repo = UserRepository(db_session)
    user = User(email="test@example.com")

    # Act
    repo.save(user)
    retrieved = repo.get_by_email("test@example.com")

    # Assert
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
```

---

## API Integration

```python
import pytest
import responses

@pytest.fixture
def mock_api():
    """Mock external API responses."""
    with responses.RequestsMock() as rsps:
        yield rsps

def test_client_fetches_user_data(mock_api):
    # Arrange
    mock_api.add(
        responses.GET,
        "https://api.example.com/users/123",
        json={"id": "123", "name": "Test User"},
        status=200,
    )
    client = ApiClient("https://api.example.com")

    # Act
    user = client.get_user("123")

    # Assert
    assert user.id == "123"
    assert user.name == "Test User"

def test_client_handles_api_error(mock_api):
    # Arrange
    mock_api.add(
        responses.GET,
        "https://api.example.com/users/123",
        json={"error": "Not found"},
        status=404,
    )
    client = ApiClient("https://api.example.com")

    # Act & Assert
    with pytest.raises(NotFoundError):
        client.get_user("123")
```

---

## File I/O Integration

```python
def test_config_loader_reads_yaml(tmp_path):
    # Arrange
    config_file = tmp_path / "config.yaml"
    config_file.write_text("database:\n  host: localhost\n  port: 5432")

    # Act
    config = ConfigLoader.load(config_file)

    # Assert
    assert config.database.host == "localhost"
    assert config.database.port == 5432
```

---

## Speed Requirements

| Type | Max Duration |
|------|--------------|
| Single integration test | < 5s |
| Integration test suite | < 5min |

---

## Markers

```python
# Mark slow integration tests
@pytest.mark.integration
@pytest.mark.slow
def test_full_pipeline_processes_batch():
    ...

# Run only unit tests (fast)
# pytest -m "not integration"

# Run all tests
# pytest
```

---

## UP

[testing/INDEX.md](INDEX.md)
