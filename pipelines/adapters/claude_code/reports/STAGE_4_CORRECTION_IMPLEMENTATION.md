# Stage 4 Gemini LLM Correction Implementation

**Date**: 2026-01-27  
**Status**: ✅ Implemented  
**Critical**: Stage 4 now corrects user messages using Gemini LLM

---

## Summary

Stage 4 has been updated to use Gemini LLM for text correction. **Only user messages are corrected**; assistant messages and thinking blocks pass through unchanged.

---

## Implementation Details

### Correction Policy

**✅ User Messages (role = 'user')**:
- Corrected using Gemini LLM
- Correction metadata stored in `metadata` JSON field
- Original text preserved in metadata for verification

**✅ Assistant Messages (role = 'assistant')**:
- Pass through unchanged
- No LLM correction applied
- Original text used as-is

**✅ Thinking Blocks (message_type contains 'thinking')**:
- Pass through unchanged
- No LLM correction applied
- Original text used as-is

### Gemini Configuration

- **Model**: `gemini-2.0-flash-exp`
- **API Key**: From `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- **Retry Logic**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Input Limit**: 8000 characters per message

### Correction Prompt

```
Correct and clean this user message text while preserving meaning, tone, and style.

Rules:
- Correct spelling, grammar, and formatting issues
- Preserve tone, emojis, and technical content (code, URLs, file paths)
- Only correct actual errors, not intentional style
- Preserve code snippets exactly
- Keep the original intent and meaning
```

### Metadata Structure

Correction metadata is stored in the `metadata` JSON field:

```json
{
  "session_id": "...",
  "message_index": 0,
  "message_type": "user",
  "role": "user",
  "model": "...",
  "cost_usd": 0.0,
  "tool_name": null,
  "original_text": "Original user message text",
  "corrected_text": "Corrected user message text",
  "changes_made": "Brief description of corrections",
  "correction_cost_usd": 0.0,
  "correction_model": "gemini-2.0-flash-exp"
}
```

For assistant/thinking messages (no correction):
```json
{
  "session_id": "...",
  "message_index": 1,
  "message_type": "assistant",
  "role": "assistant",
  "model": "...",
  "cost_usd": 0.0,
  "tool_name": null
}
```

### Error Handling

- **Gemini API failures**: Logged as warning, original text used
- **JSON parsing errors**: Logged as warning, original text used
- **Missing API key**: Raises ValueError with clear message
- **Network errors**: Retried up to 3 times with exponential backoff

### Data Persistence

- Uses `merge_rows_to_table()` for idempotent persistence
- Match key: `entity_id`
- Preserves all runs (can step back)

---

## Code Changes

### New Functions

1. **`get_gemini_client()`**: Initializes Gemini LLM client
2. **`_correct_text_impl()`**: Core correction logic (wrapped with retry)
3. **`correct_text_with_retry()`**: Retry wrapper for Gemini calls

### Modified Functions

1. **`process_staging()`**: 
   - Now queries Stage 3 data row-by-row
   - Applies Gemini correction to user messages only
   - Passes through assistant/thinking messages unchanged
   - Stores correction metadata in JSON field

### Statistics Returned

```python
{
    "input_rows": int,        # Total rows from Stage 3
    "output_rows": int,       # Total rows written to Stage 4
    "user_corrected": int,    # Number of user messages successfully corrected
    "user_failed": int,       # Number of user messages that failed correction
    "dry_run": bool
}
```

---

## Verification

The existing `verify_stage_4.py` script checks for correction metadata:
- Looks for `$.original_text` in metadata JSON
- Looks for `$.corrected_text` in metadata JSON
- Looks for `$.correction_cost_usd` in metadata JSON

This verification will now work correctly with the new implementation.

---

## Usage

### Run Stage 4
```bash
python3 pipelines/adapters/claude_code/scripts/stage_4/claude_code_stage_4.py
```

### Dry Run (Check Counts)
```bash
python3 pipelines/adapters/claude_code/scripts/stage_4/claude_code_stage_4.py --dry-run
```

### Verify Correction
```bash
python3 pipelines/adapters/claude_code/scripts/stage_4/verify_stage_4.py
```

---

## Requirements

- **Environment Variable**: `GOOGLE_API_KEY` or `GEMINI_API_KEY` must be set
- **Python Package**: `google-generativeai` must be installed
  ```bash
  pip install google-generativeai
  ```

---

## Testing Checklist

- [x] Code compiles successfully
- [ ] User messages are corrected
- [ ] Assistant messages pass through unchanged
- [ ] Thinking blocks pass through unchanged
- [ ] Correction metadata is stored correctly
- [ ] Error handling works (missing API key, network errors)
- [ ] Retry logic works for transient failures

---

## Next Steps

1. Test with actual data
2. Verify correction quality
3. Monitor API costs
4. Adjust prompt if needed

---

**Last Updated**: 2026-01-27  
**Status**: ✅ Implementation Complete
