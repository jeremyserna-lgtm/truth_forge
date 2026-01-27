# Parser Timestamp Audit — 2025-10-30

**Author:** Codex
**Scope:** Agent parsers (Codex, Copilot, Gemini Code) currently failing canonical runner validation due to missing `started_at` / message timestamp fields.

---

## 1. Schema Requirements

BigQuery core tables expect populated timestamps:

| Table | Required columns | Notes |
| --- | --- | --- |
| `spine.conversation` | `started_at TIMESTAMP` | Used for identity generation + dedupe. |
| `spine.message` | `ts TIMESTAMP` | One row per turn; canonical runner derives from parser output. |

Canonical runner (`parsers/shared/canonical_runner.py`) enforces these requirements:
```python
started_at = hooks.started_at(conversation, config)
# raises if parser hook cannot derive a timestamp
```

If `started_at` cannot be derived, the runner logs
```
Unable to derive started_at for <file>: Conversation missing timestamp information
```
and skips the conversation.

---

## 2. Parser Findings

### 2.1 Codex (`conversation_pipeline/parsers/ai_agents/codex_parser/parser.py`)
- **Current logic:** `_derive_started_at` expects `conversation['createdAt']` (or `created_at`).
- **Real exports:** JSONL files named `rollout-2025-09-30T06-45-30-....jsonl` often omit `createdAt` fields.
- **Available fallbacks:**
  1. First message timestamp (`messages[0]['timestamp']`).
  2. Filename timestamp (`rollout-YYYY-MM-DDTHH-MM-SS`) → replace trailing hyphens with colons to build ISO string.
  3. File metadata (mtime) as last resort.
- **Status:** Fails all staged files (`Unable to derive started_at`). No rows written.

### 2.2 Copilot (`conversation_pipeline/parsers/ai_agents/copilot_parser/parser.py`)
- **Current logic:** `_derive_started_at` uses `conversation['createdAt']` or `messages[0]['timestamp']`.
- **Actual file shape (per `docs/pipeline/sources/copilot_chat_local_format.md`):**
  ```json
  {
    "version": 3,
    "requests": [
      {
        "timestamp": 1729564835123,        // ms epoch
        "message": {"text": "..."},
        "response": [{"value": "..."}],
        ...
      }
    ],
    "creationDate": 1729564835123,
    "lastMessageDate": 1729564898123
  }
  ```
- **Issues:**
  - No top-level `messages` array → `_derive_started_at` sees empty list and throws.
  - Timestamps stored as ms epochs (`creationDate`, `requests[].timestamp`) rather than ISO strings.
  - Staging directory also contains non-session files (`workspace.json`, `state.json`) and sessions >100 MB.
- **Required adjustments:**
  1. `_load_conversations` must expand `requests[]` into user/assistant message sequence.
  2. Convert epoch milliseconds (`creationDate`, `requests[].timestamp`) to ISO.
  3. Skip non-conversation files and enforce size limit gracefully.
- **Status:** 108/108 staged files failed with missing timestamp error.

### 2.3 Gemini Code (`conversation_pipeline/parsers/ai_agents/gemini_code_parser/parser.py`)
- **Current logic:** `_derive_started_at` expects `conversation['created_at']`.
- **Real exports:** Files named `session-2025-10-28T00-15-53....json` lack `created_at` but include:
  - `messages[0]['timestamp']` ISO strings.
  - Timestamp embedded in filename (`session-YYYY-MM-DDTHH-MM-SS`).
- **Action:** Add fallback to first message timestamp, then filename.
- **Status:** 5/5 staged files failed with missing timestamp error.

---

## 3. Verification Commands

```bash
# Codex (fails with current logic)
./run_with_services.sh python3 conversation_pipeline/parsers/ai_agents/codex_parser/parser.py \
  --input-uri gs://conversation-archives/codex/staging/2025-10-29/ \
  --enable-bigquery-output --log-level INFO

# Copilot (fails – dataset contains chatSessions/*.json and supplemental files)
./run_with_services.sh python3 conversation_pipeline/parsers/ai_agents/copilot_parser/parser.py \
  --input-uri gs://conversation-archives/copilot/staging/2025-10-29/ \
  --enable-bigquery-output --log-level INFO

# Gemini Code (fails)
./run_with_services.sh python3 conversation_pipeline/parsers/ai_agents/gemini_code_parser/parser.py \
  --input-uri gs://conversation-archives/gemini_code/staging/2025-10-29/ \
  --enable-bigquery-output --log-level INFO
```

All three report:
```
ERROR - Unable to derive started_at for <file>: Conversation missing timestamp information
```

---

## 4. Recommended Fix Strategy (no code changes applied yet)

| Parser | Fallback strategy | Additional handling |
| --- | --- | --- |
| Codex | 1) First message timestamp<br>2) Filename regex `rollout-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})` → ISO | Ensure JSONL loader surfaces individual conversations. |
| Copilot | 1) Use `creationDate` / `lastMessageDate` (epoch ms)<br>2) Split `requests[]` into alternating user/assistant messages with per-request timestamps | Filter non-chat files (`state.json`, `workspace.json`); gracefully skip >100 MB with log. |
| Gemini Code | 1) First message timestamp<br>2) Filename regex `session-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})` | Ensure canonical conversation structure (messages array). |

Once the fallback logic is in place, re-run the above commands and assert:
- `started_at` and message `ts` fields populate.
- Dedupe / identity checks pass.
- BigQuery loads rows into `spine.conversation` and `spine.message`.

---

## 5. Next Steps
1. Implement timestamp fallback logic per parser (after approval).
2. Augment unit tests with representative samples (include filename-derived timestamps, epoch values).
3. Re-run Claude’s parser tests to confirm BigQuery loads.
4. Update documentation (`docs/pipeline/sources/*.md`) with final timestamp extraction strategy.
