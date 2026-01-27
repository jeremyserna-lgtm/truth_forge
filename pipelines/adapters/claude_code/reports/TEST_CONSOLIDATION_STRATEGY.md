# Test Consolidation Strategy

**Date**: 2026-01-27
**Current State**: 662 tests across multiple files
**Goal**: Reduce test count by 30-40% while maintaining 90%+ coverage and quality

## Analysis

### Current Test Distribution
- **Total test files**: ~40+
- **Total tests**: 662
- **Coverage**: 28.64% (target: 90%)

### Consolidation Opportunities

#### 1. **Parameterized Tests for Similar Patterns**
Many tests follow identical patterns with different inputs:
- Stage main() functions (5 separate tests → 1 parameterized test)
- Validation functions with valid/invalid inputs (12 tests → 2-3 parameterized tests)
- Edge cases across stages (multiple files → consolidated parameterized tests)

#### 2. **Fixture-Based Shared Test Utilities**
- Common mocking patterns (BigQuery client, logger, run_id)
- Shared test data generators
- Common assertion helpers

#### 3. **Integration Over Unit Tests**
- Many unit tests test isolated functions
- Integration tests can cover multiple functions in one test
- Focus on critical paths rather than exhaustive unit coverage

#### 4. **Test File Consolidation**
- Multiple "expanded" and "additional" files for same stages
- Consolidate by stage or functionality, not by test type

## Proposed Strategy

### Phase 1: Consolidate Main Function Tests
**Current**: 5 separate test functions for stages 0-4
**Proposed**: 1 parameterized test covering all stages

**Savings**: 4 tests → 1 test (80% reduction)

### Phase 2: Consolidate Validation Tests
**Current**: Multiple test files with similar validation patterns
**Proposed**: Parameterized tests grouped by validation type

**Savings**: ~20 tests → ~6 parameterized tests (70% reduction)

### Phase 3: Consolidate Edge Case Tests
**Current**: Separate edge case files per stage
**Proposed**: Consolidated edge case tests using fixtures and parameterization

**Savings**: ~50 tests → ~20 parameterized tests (60% reduction)

### Phase 4: Focus on Integration Tests
**Current**: Many isolated unit tests
**Proposed**: Prioritize integration tests that cover multiple functions

**Savings**: Replace ~100 unit tests with ~30 integration tests (70% reduction)

## Implementation Plan

1. **Create consolidated test utilities** (`test_utils.py`)
   - Shared fixtures
   - Common mocking helpers
   - Test data generators

2. **Consolidate main function tests**
   - Single parameterized test for all stage main() functions

3. **Consolidate validation tests**
   - Parameterized tests for each validation function type

4. **Consolidate edge cases**
   - Group by functionality, not by stage

5. **Focus on critical paths**
   - Integration tests for end-to-end flows
   - Unit tests only for complex logic

## Expected Results

- **Test count**: 662 → ~300-400 tests (30-40% reduction)
- **Coverage**: Maintain or improve from 28.64%
- **Quality**: Maintained through integration tests and critical path coverage
- **Maintainability**: Improved through consolidation and shared utilities

## Quality Guarantees

1. **Coverage maintained**: Integration tests cover multiple functions
2. **Critical paths tested**: All stage main() functions, validation, error handling
3. **Edge cases covered**: Through parameterized tests
4. **Integration verified**: End-to-end flows tested
5. **No regression**: All existing passing tests must still pass after consolidation
