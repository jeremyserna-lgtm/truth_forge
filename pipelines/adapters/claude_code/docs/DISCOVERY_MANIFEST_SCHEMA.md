# Discovery Manifest Schema

The **discovery manifest** is the single file produced by Stage 0. It describes everything discovered about the data source. Downstream stages read it; they do not assume or hardcode source-specific structure.

**Manifest version:** `1.0`

---

## Top-Level Keys

| Key | Type | Description |
|-----|------|-------------|
| `manifest_version` | string | Schema version, e.g. `"1.0"` |
| `source` | object | Source location and format |
| `discovery` | object | All discovered structure, counts, identifiers, primitives |
| `go_no_go` | string | `GO: ...` \| `NO-GO: ...` \| `CAUTION: ...` |
| `recommendations` | array of string | Human-readable recommendations |
| `run_id` | string | Pipeline run id |
| `assessment_timestamp` | string | ISO8601 UTC |

---

## `source`

| Key | Type | Description |
|-----|------|-------------|
| `path` | string | `--source-dir` path that was scanned |
| `format` | string | e.g. `"jsonl"` |
| `encoding` | string | e.g. `"utf-8"` |

---

## `discovery`

| Key | Type | Description |
|-----|------|-------------|
| `files_processed` | int | Number of files analyzed |
| `messages_processed` | int | Total record/message count |
| `files_per_folder` | object | `{ "<folder>": { "file_count": N, "files": [...] } }` |
| `structure` | object | `fields_top_level`, `fields_nested` (key → count) |
| `identifiers` | object | ID-like keys: `{ "<key>": { "messages_with_key": N } }` |
| `primitives` | object | Actable elements, content block types, tool names, etc. |
| `date_range` | object | `earliest`, `latest` (ISO8601) |
| `counts` | object | `thinking_blocks`, `text_blocks`, `tool_calls`, `tool_results`, etc. |
| `files_analyzed` | array | Per-file discovery details (path, counts, errors) |
| `interpretation` | object | Plain-language insights for non-coders (see below) |

**`interpretation`** (optional): `what_you_could_do` (array of string), `things_you_might_not_know` (array of string). Generated from discovery to explain what you could do with what we found, and things in the data you might not know that could change how you work.

Downstream stages use `discovery` to know what exists. They do **not** reference variables by name outside this structure.
