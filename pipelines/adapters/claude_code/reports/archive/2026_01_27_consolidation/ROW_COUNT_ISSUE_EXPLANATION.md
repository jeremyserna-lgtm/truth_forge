> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [FINAL_REASSESSMENT.md](FINAL_REASSESSMENT.md) or [ALL_STAGES_ALIGNMENT_COMPLETE.md](ALL_STAGES_ALIGNMENT_COMPLETE.md)
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Intermediate issue resolution documents. All issues resolved and documented in final reports.
>
> This document has been moved to archive. See archive location below.

---

# Row Count Issue - Explanation & Fix

**Date:** 2026-01-22  
**Issue:** Low row counts in pipeline stages

---

## The Problem

### What Should Happen
- **Stage 0:** Found 1,044 files with 79,334 messages ✅
- **Stage 1:** Should extract ALL 79,334 messages ❌
- **Stage 3:** Should process ALL messages from Stage 2 ❌

### What Actually Happened
- **Stage 1:** Only processed 59 files → 2,006 rows ❌
- **Stage 3:** Only has 12 rows (all test data) ❌

---

## Root Causes

### Issue 1: Stage 1 Only Processed 59 Files

**Why:** Stage 1 stopped processing after 59 files. This could be:
- An error that stopped processing
- A limit that was set
- A batch size issue

**Fix:** Re-run Stage 1 to process ALL 1,044 files

### Issue 2: Stage 3 Has Test Data Only

**Why:** Stage 3 was run with test data (`/tmp/s1test/a.jsonl`) instead of real data

**Fix:** Re-run Stage 3 to process the real data from Stage 2

---

## Expected Row Counts

After fixing, you should see:
- **Stage 1:** ~79,334 rows (one per message)
- **Stage 2:** ~79,334 rows (cleaned messages)
- **Stage 3:** ~79,334 rows (with entity IDs)
- **Stage 4:** ~79,334 rows (with LLM corrections)

---

## The Fix

1. **Re-run Stage 1** to process all files
2. **Re-run Stage 2** to clean all messages
3. **Re-run Stage 3** to generate IDs for all messages
4. **Re-run Stage 4** to correct text for all messages

This will process all 79,334 messages instead of just 2,006.

---

## Why This Happened

Stage 1 likely stopped early due to:
- An unhandled error
- A processing limit
- A batch size issue

Stage 3 was run with test data during development, not with the real data.

---

## Next Steps

We'll re-run the stages to process ALL your data.
