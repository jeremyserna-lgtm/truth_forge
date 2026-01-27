# Unit Tests

**Fast, focused tests for individual functions and classes.**

---

## The AAA Pattern

All tests MUST follow Arrange-Act-Assert:

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

---

## Naming Convention

`test_<function>_<scenario>_<expected>`

```python
# CORRECT - Clear what's being tested
def test_calculate_total_empty_list_returns_zero(): ...
def test_calculate_total_single_item_includes_tax(): ...
def test_calculate_total_negative_price_raises_error(): ...

# WRONG - Vague
def test_calculate(): ...
def test_it_works(): ...
```

---

## Testing Categories

### Happy Path

```python
def test_process_record_valid_input_returns_result():
    record = {"id": "123", "value": 42}
    result = process_record(record)
    assert result.success is True
    assert result.processed_value == 42
```

### Edge Cases

```python
def test_process_record_empty_dict_returns_empty_result():
    result = process_record({})
    assert result.success is True
    assert result.processed_value is None

def test_process_record_null_value_handles_gracefully():
    record = {"id": "123", "value": None}
    result = process_record(record)
    assert result.success is True
```

### Error Paths

```python
def test_process_record_invalid_type_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        process_record("not a dict")
    assert "expected dict" in str(exc_info.value)

def test_process_record_missing_id_raises_key_error():
    with pytest.raises(KeyError):
        process_record({"value": 42})
```

---

## Speed Requirements

| Type | Max Duration |
|------|--------------|
| Unit test | < 100ms |
| Single test file | < 5s |
| Full unit suite | < 60s |

---

## Isolation Rules

Tests MUST NOT:
- Depend on execution order
- Share mutable state
- Touch real databases/APIs
- Write to filesystem (use tmp_path)

```python
# CORRECT - Isolated
def test_processor_a(mock_db):
    # Has its own mock, doesn't affect other tests
    ...

def test_processor_b(mock_db):
    # Fresh mock, independent
    ...
```

---

## UP

[testing/INDEX.md](INDEX.md)
