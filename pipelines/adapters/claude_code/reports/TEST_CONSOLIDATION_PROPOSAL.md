# Test Consolidation Proposal

**Current State**: 662 tests across 40+ files
**Proposed**: ~300-400 tests (30-40% reduction) with maintained quality

## Strategy Overview

Instead of having many individual test functions, we'll use:
1. **Parameterized tests** - Combine similar tests
2. **Integration tests** - Test multiple functions together
3. **Shared test utilities** - Reduce duplication
4. **Focus on critical paths** - Prioritize important flows

## Consolidation Examples

### Example 1: Main Function Tests
**Before**: 5 separate test functions (one per stage)
```python
def test_stage_0_main_dry_run(): ...
def test_stage_1_main_dry_run(): ...
def test_stage_2_main_dry_run(): ...
def test_stage_3_main_dry_run(): ...
def test_stage_4_main_dry_run(): ...
```

**After**: 1 parameterized test
```python
@pytest.mark.parametrize("stage,module_name,process_func", [
    (0, "stage_0.claude_code_stage_0", "generate_assessment_report"),
    (1, "stage_1.claude_code_stage_1", "parse_session_file"),
    ...
])
def test_stage_main_functions_dry_run(stage, module_name, process_func): ...
```

**Savings**: 5 tests → 1 test (80% reduction)

### Example 2: Logging Bridge Tests
**Before**: 6 separate test functions
**After**: 3 parameterized tests
**Savings**: 6 tests → 3 tests (50% reduction)

### Example 3: Validation Tests
**Before**: Multiple files with similar patterns
**After**: Parameterized tests grouped by validation type
**Savings**: ~20 tests → ~6 tests (70% reduction)

## Quality Guarantees

1. **Coverage maintained**: Integration tests cover multiple functions
2. **All critical paths tested**: Main functions, validation, error handling
3. **Edge cases covered**: Through parameterization
4. **Integration verified**: End-to-end flows tested
5. **No regression**: All existing passing tests must still pass

## Implementation Plan

1. Create consolidated versions of test files
2. Verify they pass and maintain coverage
3. Replace original files
4. Update test count and coverage reports

## Expected Results

- **Test count**: 662 → ~300-400 tests
- **Coverage**: Maintain or improve from 28.64%
- **Maintainability**: Improved through consolidation
- **Quality**: Maintained through integration tests
