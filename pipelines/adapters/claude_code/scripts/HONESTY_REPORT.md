# Honesty Report: submit_all_stages_parallel.py

## All Configuration Parameters

### Function Parameters (with defaults):
- `stages: Optional[List[int]] = None` - List of stage numbers to submit (default: 0-10)
- `max_workers: int = 8` - Maximum concurrent thread workers (default: 8)
- `submission_timeout_seconds: int = 300` - Timeout per submission in seconds (default: 300 = 5 minutes)

### Hardcoded Values:
- Project root discovery: `Path(__file__).parent.parent.parent.parent` (4 levels up)
- Default stages: `list(range(11))` (stages 0-10)
- Stage file pattern: `stage_{stage_num}/claude_code_stage_{stage_num}.py`

## All Limits

### Concurrency Limits:
- **Default**: 8 concurrent submissions maximum
- **Can be overridden**: Yes, via `max_workers` parameter
- **Why limited**: Prevents resource exhaustion, system crashes, overwhelming downstream services

### Timeout Limits:
- **Per submission**: 5 minutes (300 seconds)
- **Total timeout**: `submission_timeout_seconds * len(stages)` (e.g., 55 minutes for 11 stages)
- **Can be overridden**: Yes, via `submission_timeout_seconds` parameter
- **Why limited**: Prevents deadlocks, zombie processes, infinite waiting

### Path Limits:
- **Validation**: Paths must be within project root (prevents path traversal)
- **Stage number validation**: Must be >= 0 (prevents negative numbers)

## All AI Decisions

1. **Chose 8 as default max_workers**: Industry standard for I/O-bound tasks, prevents resource exhaustion
2. **Chose 5 minutes as default timeout**: Reasonable for API calls, prevents deadlocks
3. **Used ThreadPoolExecutor**: Appropriate for I/O-bound parallel API calls
4. **Added path validation**: Prevents security vulnerabilities (path traversal)
5. **Added input validation**: Prevents invalid stage numbers
6. **Mixed logging and print**: Logging for system, print for user visibility (could be improved)
7. **Used as_completed with timeout**: Prevents deadlocks while allowing parallel execution

## All Hidden Assumptions

1. **Project structure is fixed**: Assumes script location relative to project root won't change
2. **Stages are numbered 0-10**: Assumes pipeline has exactly 11 stages
3. **File naming is consistent**: Assumes all stages follow `claude_code_stage_{num}.py` pattern
4. **review_object handles reviewer limits**: Assumes review_object ensures reviewers see entire files (it does)
5. **5 minutes is enough**: Assumes most submissions complete within 5 minutes
6. **8 workers is safe**: Assumes system can handle 8 concurrent API calls

## What Reviewers See

**Reviewers have NO LIMITS on what they can see:**
- ✅ Entire file (no chunking, no truncation)
- ✅ All configuration parameters (shown in this report)
- ✅ All limits (shown in this report)
- ✅ All AI decisions (shown in this report)
- ✅ All assumptions (shown in this report)

This is handled by `review_object()` function, which ensures reviewers see complete files.
