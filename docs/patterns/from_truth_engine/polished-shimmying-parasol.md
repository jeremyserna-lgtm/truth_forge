---
title: "Markdown Declutter - Move to GCS"
type: patterns
category: patterns
status: active
tags: ['markdown', 'migration', 'GCS']
created: 2026-01-06T18:59:34.790172+00:00
summary: "Migrate local markdown files to a Google Cloud Storage bucket."
---

# Plan: Markdown Declutter - Move to GCS

## The Problem

**Markdown sprawl is causing confusion.** Files everywhere. Hard to find anything.

## The Goal

Move all non-framework markdown files to GCS bucket, organized for later processing.

**Two folders in the bucket:**
- `not_processed/` - Files awaiting atom extraction
- `processed/` - Files that have been extracted (moved here later, by separate job)

## Scope: What Gets Moved

| Category | Count | Action |
|----------|-------|--------|
| corpus/ | 9,688 | MOVE to GCS |
| architect_central_services/docs/ | 570 | MOVE to GCS |
| docs/* (except framework) | ~500 | MOVE to GCS |
| _deprecated/ | 297 | MOVE to GCS |
| pipeline docs | ~100 | MOVE to GCS |
| **Total** | **~11,000** | |

## Exclusions: What Stays Local

| Pattern | Why |
|---------|-----|
| `docs/the_framework/**` | Foundation, per request |
| `.claude/rules/**` | Active governance |
| `**/README.md` | Navigation |
| `CLAUDE.md` | Identity |
| `**/*.cursor/**` | IDE config |

## Bucket Structure

```
gs://primitive_engine_library/
├── not_processed/                    # Landing zone
│   ├── corpus/                       # External ingested docs
│   ├── architect_central_services/   # Project docs
│   │   └── docs/                     # The 570-file sprawl
│   ├── docs/                         # General docs
│   │   ├── architecture/
│   │   ├── business/
│   │   └── ...
│   ├── _deprecated/                  # Already archived locally
│   └── pipelines/                    # Pipeline-specific docs
│
└── processed/                        # After atom extraction (future)
    └── {same structure}
```

## The Script: `scripts/migrate_markdown_to_gcs.py`

```python
"""
Migrate local markdown files to GCS bucket.

HOLD₁ (local markdown) → AGENT (upload) → HOLD₂ (GCS bucket)

Usage:
    python scripts/migrate_markdown_to_gcs.py --dry-run  # Preview
    python scripts/migrate_markdown_to_gcs.py            # Execute
    python scripts/migrate_markdown_to_gcs.py --resume   # Resume from checkpoint
"""
from pathlib import Path
from architect_central_services import get_logger, get_current_run_id
from architect_central_services.core.shared import get_gcs_client

BUCKET = "primitive_engine_library"
DEST_PREFIX = "not_processed"
MANIFEST_PATH = Path("data/markdown_migration_manifest.jsonl")

# Exclusion patterns (stay local)
EXCLUDE_PATTERNS = [
    "docs/the_framework/**",
    ".claude/rules/**",
    "**/README.md",
    "CLAUDE.md",
    "node_modules/**",
    "frontend/node_modules/**",
]

def main():
    client = get_gcs_client()

    for md_file in glob_all_markdown():
        if is_excluded(md_file):
            continue

        dest_path = f"{DEST_PREFIX}/{relative_path(md_file)}"

        # Upload
        result = client.upload_blob(
            bucket_name=BUCKET,
            source_file_path=str(md_file),
            destination_blob_name=dest_path,
            tool_name="markdown_migration"
        )

        # Log to manifest
        write_manifest_entry(md_file, dest_path, result)
```

### Key Features

1. **Dry-run first** - See what would move without moving
2. **Checkpointed** - Can resume if interrupted
3. **Manifest** - JSONL log of what moved where
4. **Preserves structure** - Local path → bucket path mapping
5. **Git cleanup** - After successful upload, `git rm` local files

## Implementation Steps

### Step 1: Create Migration Script
- Central services integration
- Glob all markdown files
- Filter exclusions
- Upload to `not_processed/` prefix
- Write manifest

### Step 2: Dry Run
- Run with `--dry-run`
- Review file list
- Confirm scope

### Step 3: Execute Migration
- Run for real
- Checkpoint progress
- Upload files

### Step 4: Verify
- Check GCS bucket
- Compare manifest to bucket contents
- Confirm all files present

### Step 5: Local Cleanup
- `git rm` all migrated files
- Commit removal

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/migrate_markdown_to_gcs.py` | Main migration script |
| `data/markdown_migration_manifest.jsonl` | What moved where |

## Manifest Schema (Every File Tracked)

```jsonl
{
  "source_path": "/Users/jeremyserna/PrimitiveEngine/architect_central_services/docs/KNOWLEDGE_ATOMS_SYSTEM_OVERVIEW.md",
  "source_dir": "architect_central_services/docs",
  "filename": "KNOWLEDGE_ATOMS_SYSTEM_OVERVIEW.md",
  "destination_bucket": "primitive_engine_library",
  "destination_path": "not_processed/architect_central_services/docs/KNOWLEDGE_ATOMS_SYSTEM_OVERVIEW.md",
  "file_size_bytes": 8234,
  "md5_hash": "abc123...",
  "uploaded_at": "2026-01-02T10:30:00Z",
  "upload_status": "success",
  "local_deleted": false,
  "run_id": "run_abc123"
}
```

**Every file gets a line.** Before upload, during upload, after upload.

The manifest IS the source of truth for the migration.

## Cost Estimate

- GCS storage: ~$0.02/GB/month
- Estimated size: ~50MB of markdown → $0.001/month
- Upload: Free within project

**Essentially free.**

## Post-Migration: Atom Extraction (Separate Job)

Once files are in GCS, a separate job will:
1. Read from `not_processed/`
2. Extract knowledge atoms
3. Store atoms in BigQuery
4. Move file to `processed/`

This is decoupled from the migration itself.
