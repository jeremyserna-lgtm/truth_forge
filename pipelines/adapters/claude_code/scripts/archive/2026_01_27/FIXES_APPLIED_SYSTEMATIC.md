> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [ALL_FIXES_COMPLETE.md](ALL_FIXES_COMPLETE.md)
> - **Deprecated On**: 2026-01-27
> - **Sunset Date**: TBD
> - **Reason**: Consolidated into comprehensive fix documentation. See ALL_FIXES_COMPLETE.md for complete fix history.
>
> This document is retained for historical reference and lineage tracking.

---

# Systematic Fixes Applied - Line-by-Line

**Date**: 2026-01-23  
**Status**: 🚨 **DEPRECATED - SUPERSEDED BY ALL_FIXES_COMPLETE.md**  
**Approach**: Read each review issue line-by-line, fix exact code, verify fix, check for similar issues

## Fixes Applied

### ✅ Fix 1: Stage 3 Line 385 - Use Validated Table ID

**Reviewer Issue**: Line 298 uses unvalidated `STAGE_3_TABLE` constant instead of `validated_stage_3_table`

**Actual Location**: Line 385 (code may have shifted)

**Fix Applied**:
```python
# BEFORE:
table_id=STAGE_3_TABLE,

# AFTER:
table_id=validated_stage_3_table,
```

**Verification**: ✅ Fixed - now uses validated variable that was already created on line 236

**Similar Issues Checked**: 
- ✅ Stage 3 line 373: Already uses `validated_stage_3_table` (correct)
- ✅ Other stages: Checked for similar patterns

---

### ✅ Fix 2: Stage 14 Line 597 - Timestamp SQL Injection

**Reviewer Issue**: Line 467 (actual line 597) uses f-string interpolation for timestamp without validation

**Fix Applied**:
```python
# BEFORE:
promoted_at_str = promoted_at.strftime("%Y-%m-%d %H:%M:%S")
select_parts.append(f"TIMESTAMP('{promoted_at_str}') AS promoted_at")

# AFTER:
# FIX: Validate and escape timestamp to prevent SQL injection
if not isinstance(promoted_at, datetime):
    raise ValueError(f"promoted_at must be datetime object, got {type(promoted_at)}")
# Use ISO format which is safe for BigQuery TIMESTAMP()
promoted_at_iso = promoted_at.strftime("%Y-%m-%d %H:%M:%S")
# Validate format contains only safe characters (digits, hyphens, colons, spaces)
import re
if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', promoted_at_iso):
    raise ValueError(f"Invalid timestamp format: {promoted_at_iso}")
# Use validated timestamp - BigQuery TIMESTAMP() function safely handles properly formatted strings
select_parts.append(f"TIMESTAMP('{promoted_at_iso}') AS promoted_at")
```

**Verification**: ✅ Fixed - timestamp is now validated before use

**Similar Issues Checked**:
- ✅ Stage 16 line 224: Fixed with same validation pattern
- ✅ Other stages: Checked for timestamp interpolation

---

### ✅ Fix 3: Stage 16 Line 224 - Timestamp SQL Injection

**Reviewer Issue**: Similar timestamp interpolation issue in `_build_merge_query()`

**Fix Applied**: Same validation pattern as Stage 14

**Verification**: ✅ Fixed

---

## Issues Still Pending

### ⏳ Stage 2 Lines 157-158 - CREATE TABLE SQL Injection

**Reviewer Issue**: Uses f-string interpolation for CREATE TABLE statement

**Status**: Under review - Stage 2 already uses `validated_stage_2_table` which is validated. The reviewer's concern is that even validated table IDs can contain injection payloads if validation fails silently. However, `validate_table_id()` raises exceptions on invalid input, so this should be safe. Need to verify the validation is strict enough.

**Current Code**:
```python
validated_stage_2_table = validate_table_id(STAGE_2_TABLE)
cleaning_query = f"""
CREATE OR REPLACE TABLE `{validated_stage_2_table}`
```

**Analysis**: The table ID is validated before use. The validation function raises exceptions on invalid input, so this should be safe. However, the pattern of f-string SQL construction is still a concern. For DDL statements like CREATE TABLE, BigQuery doesn't support parameterized queries, so this is the standard approach.

**Action**: Verify `validate_table_id()` is strict enough (it is - checks regex and dangerous patterns).

---

### ⏳ Stage 14 Lines 367, 421, 445, 498 - Other SQL Interpolation Points

**Reviewer Issue**: Multiple other f-string SQL interpolation points

**Status**: Need to check each location:
- Line 367: Need to check
- Line 421: Need to check  
- Line 445: Need to check
- Line 498: Need to check

**Action**: Check each line and fix if needed.

---

### ⏳ Path Traversal - Stages 0 and 1

**Reviewer Issue**: Environment variable bypass in path validation

**Status**: Need to review and fix

---

### ⏳ Memory Issues - Stages 0, 6, 10

**Reviewer Issue**: Loading entire datasets into memory

**Status**: Need to implement streaming

---

## Next Steps

1. Continue checking Stage 14 other SQL interpolation points
2. Review Stage 2 CREATE TABLE validation
3. Fix path traversal issues
4. Fix memory issues
