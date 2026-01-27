# Test Consolidation Actions

## Immediate Actions to Remove Duplicates

### 1. Deprecate Legacy Files (Superseded by Comprehensive)
These files are superseded by newer comprehensive test files:
- `test_stage_4_5_6_7.py` → Covered by `test_stage_4_5_comprehensive.py`, `test_stage_6_11_13_comprehensive.py`, `test_stage_7_14_comprehensive.py`
- `test_stage_8_9_10_11_12.py` → Covered by `test_stage_8_9_10_12_comprehensive.py`, `test_stage_6_11_13_comprehensive.py`
- `test_stage_13_14_15_16.py` → Covered by `test_stage_13_comprehensive.py`, `test_stage_7_14_comprehensive.py`, `test_stage_15_16_comprehensive.py`

### 2. Remove Duplicate Test Functions
For functions tested in multiple files, keep only:
- **Comprehensive version** in `*_comprehensive.py`
- **Edge case version** in `*_expanded.py` or `*_final.py`
- Remove duplicates from other files

### 3. Consolidate Shared Utilities Tests
Merge into 2 files:
- `test_shared_utilities_comprehensive.py` - All main coverage
- `test_shared_utilities_edge_cases.py` - All edge cases

### 4. Consolidate Logging Bridge Tests
Merge into 1 file:
- `test_shared_logging_bridge_comprehensive.py` - All coverage

### 5. Consolidate Check Errors Tests
Merge into 1 file:
- `test_shared_check_errors_comprehensive.py` - All coverage

## Functions with Excessive Duplication

### parse_session_file (12 files → Target: 2-3 files)
- Keep: `test_stage_0_comprehensive.py::test_stage_0_parse_session_file`
- Keep: `test_stage_0_expanded.py::test_stage_0_parse_session_file_edge_cases`
- Keep: `test_stage_1_11_13_final.py::test_stage_1_parse_session_file_comprehensive` (stage 1 version)
- Remove: All other duplicates

### clean_content (7 files → Target: 2 files)
- Keep: `test_stage_2_7_final.py::test_stage_2_clean_content_comprehensive`
- Keep: `test_stage_1_2_expanded.py::test_stage_2_clean_content_edge_cases`
- Remove: All other duplicates

### normalize_timestamp (7 files → Target: 2 files)
- Keep: `test_stage_2_7_final.py::test_stage_2_normalize_timestamp_comprehensive`
- Keep: `test_stage_1_2_expanded.py::test_stage_2_normalize_timestamp_edge_cases`
- Remove: All other duplicates

### chunk_list (6 files → Target: 2 files)
- Keep: `test_shared_utilities_comprehensive.py` (when consolidated)
- Keep: `test_shared_utilities_edge_cases.py` (when consolidated)
- Remove: All duplicates from other files

### safe_json_loads (6 files → Target: 2 files)
- Keep: `test_shared_utilities_comprehensive.py` (when consolidated)
- Keep: `test_shared_utilities_edge_cases.py` (when consolidated)
- Remove: All duplicates from other files

### create_fingerprint (6 files → Target: 2 files)
- Keep: `test_shared_utilities_comprehensive.py` (when consolidated)
- Keep: `test_shared_utilities_edge_cases.py` (when consolidated)
- Remove: All duplicates from other files

### validate_entity (8 files → Target: 2 files)
- Keep: `test_stage_15_16_comprehensive.py::test_stage_15_validate_entity_comprehensive`
- Keep: `test_stage_9_15_expanded.py::test_stage_15_validate_entity_edge_cases`
- Remove: All other duplicates

## Next Steps
1. Review each duplicate to ensure no unique coverage is lost
2. Remove redundant test functions
3. Deprecate legacy files
4. Verify coverage remains at 90%+
5. Update test file organization
