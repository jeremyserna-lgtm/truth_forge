> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [ALL_FIXES_COMPLETE.md](ALL_FIXES_COMPLETE.md)
> - **Deprecated On**: 2026-01-27
> - **Sunset Date**: TBD
> - **Reason**: Intermediate summary. See ALL_FIXES_COMPLETE.md for complete fix history and all resolved issues.
>
> This document is retained for historical reference and lineage tracking.

---

# Remaining Issues Summary - 2026-01-23

**Status**: 🚨 **DEPRECATED - SUPERSEDED BY ALL_FIXES_COMPLETE.md**

## Critical Issues by Category

### 1. Verification Scripts (CRITICAL - Most Common Issue)

**Problem**: Reviewers say verification scripts are:
- Too technical for non-coders
- Logically flawed (some check wrong things)
- Missing comprehensive checks
- Require command-line knowledge

**Specific Issues**:
- **Stage 2**: Only checks table exists, not correctness of transformations
- **Stage 3**: Checks for duplicate entity_ids but fails on re-runs (not run_id-aware)
- **Stage 4**: Doesn't check metadata field to confirm correction occurred
- **Stage 5**: Checks for level=5 but should check level=8 (documentation mismatch)
- **Stage 13**: Performs no actual verification, just prints static text
- **Stage 15**: Requires shell commands, not accessible to non-coders

**Solution Needed**: 
- Make verification scripts truly non-coder friendly (GUI or simple one-command execution)
- Fix logical errors (check correct fields, be run_id-aware)
- Add comprehensive checks (not just table existence)

### 2. Trust Reports (CRITICAL)

**Problem**: Trust reports contain:
- Technical jargon and command-line instructions
- Incorrect information (wrong stage descriptions)
- Rollback instructions requiring `bq` commands and `git` commands
- Not accessible to non-coders

**Specific Issues**:
- **Stage 2, 3, 4, 5, 6**: Rollback instructions require `bq query` and `git checkout` commands
- **Stage 5**: Trust reports say "L5 Message Processing" but code creates "L8 Conversations"
- **Stage 6**: Trust reports are too technical

**Solution Needed**:
- Create `rollback_stage_X.py` scripts (simple Python scripts, no command-line)
- Update TRUST_REPORT.md to use scripts instead of commands
- Fix factual inaccuracies in all trust reports
- Make all reports plain-language, no technical jargon

### 3. SQL Injection Concerns (HIGH)

**Problem**: Reviewers still concerned about:
- F-string interpolation even with `validate_table_id()`
- Cannot see implementation of `validate_table_id()` (black box)
- Some patterns still use f-strings

**Specific Issues**:
- **Stage 2**: Lines 157-158 validate but then use f-string interpolation
- **Stage 3**: Uses f-strings for table names, validation function not provided
- **Stage 15**: SQL injection vulnerability flagged

**Solution Needed**:
- Provide source code for `validate_table_id()` and all shared validation functions
- Document why f-strings are safe with validation (BigQuery limitation)
- Consider parameterized queries where possible

### 4. Memory Management (HIGH)

**Problem**: Reviewers claim:
- Code loads entire datasets into memory
- Unbounded aggregations (STRING_AGG)
- Will cause memory exhaustion

**Specific Issues**:
- **Stage 5**: Unbounded STRING_AGG operations can cause memory exhaustion
- **Stage 6**: Reviewers claim code loads all messages into memory (but we have streaming!)
- **Stage 4**: Should use streaming instead of loading entire table

**Solution Needed**:
- Document that streaming is already implemented (reviewers may be looking at old code)
- Fix Stage 5 STRING_AGG to be bounded
- Add comments explaining streaming approach

### 5. Turn Boundary Logic (MEDIUM)

**Problem**: Reviewers claim:
- Logic contradicts documentation
- Incorrectly closes turns

**Specific Issues**:
- **Stage 6**: Reviewers say logic is wrong, but we verified it's correct

**Solution Needed**:
- Add more explicit documentation explaining turn boundary logic
- Add comments in code showing how it matches documentation

### 6. Error Handling (MEDIUM)

**Problem**: 
- Not all errors have friendly messages
- Some stack traces can reach users
- Inconsistent error handling

**Solution Needed**:
- Add global try/except in main() to catch all errors
- Ensure all errors have "What this means" and "What to do" sections
- Standardize error handling across all stages

### 7. Documentation Mismatches (CRITICAL)

**Problem**:
- **Stage 5**: Documentation says "L8 Conversations" but code creates level=5 entities
- Trust reports have wrong stage descriptions
- Header comments contradict actual implementation

**Solution Needed**:
- Fix Stage 5: Either change code to level=8 OR update all docs to level=5
- Fix all trust reports to match actual implementation
- Remove contradictory comments

### 8. Missing Source Code (HIGH)

**Problem**: Reviewers cannot see:
- `shared_validation.py` functions
- `shared` module functions
- `src.services.central_services` imports

**Solution Needed**:
- Include all shared modules in review submissions
- Or document that these are reviewed separately

## Priority Fixes

### Immediate (Must Fix Before Acceptance):
1. ✅ Fix verification scripts (logical errors, non-coder friendly)
2. ✅ Create rollback scripts (replace bq/git commands)
3. ✅ Fix Stage 5 level mismatch (code vs docs)
4. ✅ Fix trust reports (remove technical jargon, fix inaccuracies)
5. ✅ Fix Stage 5 STRING_AGG memory issue

### High Priority:
6. ✅ Provide shared module source code or documentation
7. ✅ Fix all error handling (global try/except, friendly messages)
8. ✅ Document streaming approach (reviewers may not see it)

### Medium Priority:
9. ✅ Add more explicit turn boundary documentation
10. ✅ Enhance verification scripts with comprehensive checks

---

**Total Issues**: ~100+ across all stages
**Critical Issues**: ~30-40 that block acceptance
**Most Common**: Verification scripts and trust reports not non-coder friendly
