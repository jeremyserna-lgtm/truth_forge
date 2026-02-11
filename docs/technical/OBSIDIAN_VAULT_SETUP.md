---
id: OBSIDIAN_VAULT_SETUP
title: "Obsidian Vault Setup"
type: guide
status: canonical
domain: infrastructure
created: 2026-02-01
updated: 2026-02-01
author: claude
related:
  - METADATA
tags:
  - obsidian
  - document-management
  - knowledge-graph
---

# Obsidian Vault Setup

**How to use truth_forge as an Obsidian vault for visual navigation and knowledge graph.**

---

## Quick Start

### 1. Open truth_forge as Vault

```bash
# Obsidian can open any folder as a vault
# Just open Obsidian → Open folder as vault → select ~/truth_forge
```

Or from command line:
```bash
open -a "Obsidian" ~/truth_forge
```

### 2. Configure .gitignore

Add to `.gitignore`:
```
# Obsidian
.obsidian/
```

The `.obsidian/` folder contains personal settings (themes, plugins, workspace state). These should NOT be shared.

### 3. Install Recommended Plugins

**Required:**
- **Dataview** - Query frontmatter like a database
- **Templater** - Generate frontmatter templates

**Recommended:**
- **Graph Analysis** - Enhanced graph visualization
- **Breadcrumbs** - Navigate relationships
- **Tag Wrangler** - Manage tags
- **Linter** - Format frontmatter consistently

**Optional (AI Integration):**
- **Obsidian Copilot** - AI assistant with vault context
- **Agent Client** - Claude Code inside Obsidian

---

## Folder Configuration

In Obsidian Settings → Files & Links:

| Setting | Value | Why |
|---------|-------|-----|
| Default location for new notes | `docs/` | Keep docs organized |
| Attachment folder path | `assets/` | Images, PDFs separate |
| Use [[Wikilinks]] | ON | Enable graph relationships |
| Detect all file extensions | ON | See all files |

---

## Dataview Queries

With frontmatter per [[METADATA]], you can query the vault:

### All Specifications

```dataview
TABLE title, status, domain, updated
FROM "docs" OR "framework"
WHERE type = "specification"
SORT updated DESC
```

### Not-Me Documents

```dataview
TABLE title, type, status
FROM "docs"
WHERE domain = "not-me"
SORT title ASC
```

### Documents Needing Review

```dataview
TABLE title, last_reviewed, status
FROM "docs" OR "framework"
WHERE status = "draft" OR status = "review"
```

### Relationship Map

```dataview
TABLE title, related, supersedes
FROM "docs"
WHERE related
```

---

## Graph View Configuration

In Graph View settings:

| Setting | Recommended |
|---------|-------------|
| Show tags | ON |
| Show attachments | OFF |
| Show orphans | ON (to find disconnected docs) |
| Link thickness | Based on connections |

### Color Groups

Create color groups based on document type:
- **Blue** - `path:framework/` (framework docs)
- **Green** - `tag:#not-me` (Not-Me docs)
- **Orange** - `tag:#plan` (Business plans)
- **Red** - `tag:#deprecated` (Deprecated docs)

---

## Template: New Document

Create `templates/document.md`:

```markdown
---
id: {{title}}
title: "{{title}}"
type: specification
status: draft
domain:
created: {{date}}
updated: {{date}}
author: jeremy
related: []
tags: []
---

# {{title}}

**[One sentence describing what this document is]**

---

## Content

---

## Related Documents

---

## UP

[[INDEX]]
```

Configure Templater to use this when creating new notes.

---

## Agent Workflow

### Claude Code + Obsidian Split

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PARALLEL WORKFLOWS                                       │
│                                                                              │
│   OBSIDIAN (Your View)                CLAUDE CODE (Agent View)              │
│   ─────────────────────               ────────────────────────              │
│   • Navigate graph visually           • Bulk operations                     │
│   • Quick lookup by search            • Add frontmatter to all docs         │
│   • See relationships                 • Validate relationships              │
│   • Create new docs from template     • Generate index                      │
│   • Review/approve changes            • Restructure folders                 │
│                                                                              │
│                        SAME FILES ON DISK                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Index Generator Script

Run periodically to maintain index:

```bash
# Full scan and validation
python scripts/document_index.py

# Generate Obsidian-compatible index note
python scripts/document_index.py --obsidian

# Add frontmatter to docs missing it
python scripts/document_index.py --add-frontmatter --dry-run
python scripts/document_index.py --add-frontmatter  # Actually do it

# Export graph for external tools
python scripts/document_index.py --graph
```

---

## Wikilink Conventions

Use wikilinks in document body for relationships:

```markdown
See [[NOT_ME_CORE_SPECIFICATION]] for identity definition.

This implements [[ADR-0001|folder structure decision]].

Related: [[NOT_ME_INFRASTRUCTURE_PLAN]], [[TRUTH_ENGINE_BUSINESS_PLAN]]
```

- Use `[[doc_id]]` to link
- Use `[[doc_id|display text]]` for custom display text
- These create graph edges automatically
- Claude Code can parse these with regex

---

## Migration Steps

To migrate existing docs to this system:

### Step 1: Run Index Generator (Dry Run)

```bash
python scripts/document_index.py --add-frontmatter --dry-run
```

Review what would be changed.

### Step 2: Add Frontmatter

```bash
python scripts/document_index.py --add-frontmatter
```

This adds minimal frontmatter to docs missing it.

### Step 3: Review and Enhance

Open Obsidian, review each document:
1. Verify `type` is correct
2. Add `related` links
3. Add meaningful `tags`
4. Set `status` appropriately

### Step 4: Generate Index

```bash
python scripts/document_index.py --obsidian
```

Creates `docs/DOCUMENT_INDEX.md` with Dataview queries.

### Step 5: Validate

```bash
python scripts/document_index.py --validate
```

Fix any errors or warnings.

---

## Maintenance

| Task | Frequency | Command |
|------|-----------|---------|
| Validate relationships | Weekly | `python scripts/document_index.py --validate` |
| Regenerate index | After major changes | `python scripts/document_index.py --obsidian` |
| Review drafts | Weekly | Dataview query for `status = "draft"` |
| Check orphans | Monthly | Graph view with orphans visible |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Graph shows no connections | Check wikilinks use `[[id]]` not markdown links |
| Dataview queries empty | Install Dataview plugin, verify frontmatter format |
| Frontmatter not parsing | Check YAML validity (no tabs, proper indentation) |
| Duplicate IDs | Run `--validate`, fix duplicates manually |

---

## UP

[[INDEX]]
