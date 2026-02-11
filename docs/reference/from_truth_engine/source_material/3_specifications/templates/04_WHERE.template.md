# {SYSTEM_NAME}: Where It Lives

**Doc ID**: doc:{CATEGORY}:primitive:04:where
**Series**: PRIMITIVE
**System**: {SYSTEM_NAME}

---

## TL;DR

- Code: `{CODE_PATH}`
- Data: `{DATA_LOCATION}`
- Docs: `{DOCS_PATH}`

---

## Code Locations

| Type | Path |
|------|------|
| Source | `{SOURCE_PATH}` |
| Tests | `{TESTS_PATH}` |
| Config | `{CONFIG_PATH}` |
| Scripts | `{SCRIPTS_PATH}` |

---

## Data Locations

| Type | Location | Description |
|------|----------|-------------|
| BigQuery | `{PROJECT}.{DATASET}.{TABLE}` | {DESCRIPTION} |
| Local | `{LOCAL_PATH}` | {DESCRIPTION} |
| GCS | `gs://{BUCKET}/{PATH}` | {DESCRIPTION} |

---

## Documentation Locations

| Type | Path |
|------|------|
| Primitive series | `{SYSTEM}/docs/primitive/` |
| Specifications | `{SYSTEM}/docs/spec/` |
| Reference | `{SYSTEM}/docs/ref/` |
| Operations | `{SYSTEM}/docs/ops/` |

---

## Related Systems (Physical Proximity)

| System | Location | Connection |
|--------|----------|------------|
| {RELATED_1} | `{PATH}` | {HOW_CONNECTED} |
| {RELATED_2} | `{PATH}` | {HOW_CONNECTED} |

---

## Related

- [How It Works](03_HOW.md)
- [When To Use](05_WHEN.md)
