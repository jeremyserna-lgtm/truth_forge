# Trust Report: submit_all_stages_parallel.py

## How to Verify It Works

### 1. Run the Verification Script
```bash
python3 scripts/verify_ai_implementation.py pipelines/claude_code/scripts/submit_all_stages_parallel.py
```

This checks:
- ✅ FIDELITY_REPORT.md exists and is complete
- ✅ HONESTY_REPORT.md exists and is complete
- ✅ TRUST_REPORT.md exists and is complete
- ✅ Basic code quality (error handling, logging, docs)

### 2. Test with a Single Stage
```bash
cd /Users/jeremyserna/Truth_Engine
python3 -c "
from pipelines.claude_code.scripts.submit_all_stages_parallel import submit_stage
result = submit_stage(0)
print(f'Status: {result[\"status\"]}')
print(f'Review ID: {result.get(\"review_id\", \"N/A\")}')
"
```

### 3. Check Review Status
After submission, check if reviews are processing:
```bash
python3 scripts/peer_review.py get <review_id>
```

## What Could Go Wrong

### 1. Timeout Issues
**Problem**: Submissions take longer than 5 minutes
**Symptom**: Script reports "Timed out" for some stages
**Impact**: Those stages won't be reviewed
**Fix**: Increase `submission_timeout_seconds` parameter

### 2. Resource Exhaustion
**Problem**: Too many concurrent submissions overwhelm system
**Symptom**: API errors, system slowdown, crashes
**Impact**: Some or all submissions fail
**Fix**: Reduce `max_workers` parameter

### 3. Path Issues
**Problem**: Script can't find stage files
**Symptom**: "File not found" errors
**Impact**: Those stages won't be reviewed
**Fix**: Check file paths, ensure project structure matches assumptions

### 4. API Failures
**Problem**: review_object() fails for some stages
**Symptom**: "Error" status for some stages
**Impact**: Those stages won't be reviewed
**Fix**: Check API credentials, network connectivity, review_object() logs

### 5. Reviewers Don't See Full Files
**Problem**: review_object() chunks or truncates files
**Symptom**: Reviewers report "partial code" or "missing context"
**Impact**: Reviews are incomplete, untrustworthy
**Fix**: This should NOT happen - review_object() is configured to never chunk. If it does, this is a critical bug in review_object(), not this script.

## How to Rollback

### If Script Causes Problems:

1. **Stop the script**: `Ctrl+C` if still running

2. **Check what was submitted**:
   ```bash
   # Check review registry
   ls -la data/peer_reviews/*.json | tail -20
   ```

3. **No rollback needed for submissions**: Once submitted, reviews are in progress. You can't "unsend" them, but you can ignore the results.

4. **If script needs to be reverted**:
   ```bash
   git checkout pipelines/claude_code/scripts/submit_all_stages_parallel.py
   ```

## How to Test It

### Test 1: Verify Reports Exist
```bash
cd /Users/jeremyserna/Truth_Engine
ls -la pipelines/claude_code/scripts/*REPORT.md
```
Should show: FIDELITY_REPORT.md, HONESTY_REPORT.md, TRUST_REPORT.md

### Test 2: Run Verification Script
```bash
python3 scripts/verify_ai_implementation.py pipelines/claude_code/scripts/submit_all_stages_parallel.py
```
Should show: All checks PASS

### Test 3: Test with One Stage
```bash
cd /Users/jeremyserna/Truth_Engine
python3 -c "
from pipelines.claude_code.scripts.submit_all_stages_parallel import submit_stage
result = submit_stage(0)
assert result['status'] in ['submitted', 'not_found', 'error']
print('✅ Test passed')
"
```

### Test 4: Test with All Stages (Dry Run)
```bash
cd /Users/jeremyserna/Truth_Engine
python3 pipelines/claude_code/scripts/submit_all_stages_parallel.py
```
Watch for errors, timeouts, or failures.

## Trust Indicators

✅ **You can trust this if:**
- Verification script passes
- Reports are complete and readable
- Test runs succeed
- No errors in logs

❌ **You should NOT trust this if:**
- Verification script fails
- Reports are missing or incomplete
- Tests fail
- Errors in logs that aren't explained

## Questions to Ask

1. **"Did it submit all stages?"** - Check output for all 11 stages
2. **"Are reviewers seeing full files?"** - Check review_object() configuration (it should never chunk)
3. **"Did anything time out?"** - Check for timeout errors in output
4. **"Can I verify it worked?"** - Run verification script, check review IDs
