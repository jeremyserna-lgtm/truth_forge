---
document_id: 64bbb99c
source_file_path: /Users/jeremyserna/PrimitiveEngine/docs/recent_era_docs/JEREMY_WORKSPACE.md
source_era: recent
created_date: '2025-10-25'
version: 0.1.0
tags:
- recent_era
- legacy_document
is_legacy: true
date_extraction_confidence: content
changelog:
- timestamp: '2025-11-08T12:25:29.571344+00:00'
  author: Truth Engine V2 Shredder
  description: 'Legacy document ingested from JEREMY_WORKSPACE.md (date_source: content)'
---

# Jeremy's Workspace - The Only Folder That Matters

**Location**: `/Users/jeremyserna/Architect Library/JEREMY/`

**Purpose**: The ONLY place Jeremy needs to look. Everything else is in the database for AIs to query.

---

## The Five Files (Jeremy's Notepad)

```
/JEREMY/
├── 1_WHERE_ARE_WE.md          ← Current status, always updated
├── 2_WHATS_NEXT.md            ← Next 3 tasks, simple list
├── 3_PROBLEMS.md              ← Issues I'm seeing, needs fixing
├── 4_IDEAS.md                 ← Random thoughts, future plans
└── 5_DECISIONS_NEEDED.md      ← What I need to approve
```

**That's it. Five files. Always current. Human-readable.**

---

## How It Works

### 1. WHERE_ARE_WE.md
```markdown
# Current Status (Updated: 2025-10-25 2:30pm)

We're waiting on Codex to validate baseline enrichment.

Grok finished adding VADER, KeyBERT, BERTopic.
When Codex approves, we start Phase 1 (add checksums).

Goal: Job search data ready in 3 weeks.
```

**Who updates**: Claude (after every milestone)
**Jeremy reads**: When he wants to know where we are

---

### 2. WHATS_NEXT.md
```markdown
# Next 3 Tasks

1. Codex validates baseline enrichment (TODAY)
2. Grok adds checksum/quality/lineage fields (2-3 days)
3. Start shredding old docs to BigQuery (next week)
```

**Who updates**: Claude (after every task completes)
**Jeremy reads**: When he wants to know what's happening next

---

### 3. PROBLEMS.md
```markdown
# Current Problems

- Too many planning documents (fixing with shredding pipeline)
- Can't find the plan (fixed with START_HERE doc)

# Resolved
- ~~Analyzers not standardized~~ (Grok fixed)
```

**Who updates**: Jeremy adds, Claude/Codex/Grok resolve
**Jeremy reads**: When something feels wrong

---

### 4. IDEAS.md
```markdown
# Future Ideas

- Shred documents to metadata ← DOING THIS NOW
- Query BigQuery instead of reading docs
- Hash-based document lifecycle
```

**Who updates**: Jeremy (whenever inspiration hits)
**Jeremy reads**: When planning long-term

---

### 5. DECISIONS_NEEDED.md
```markdown
# Decisions Needed

[NONE RIGHT NOW]

# Recent Decisions
- Approved baseline enrichment upgrades (2025-10-25)
- Approved document deprecation pipeline (2025-10-25)
```

**Who updates**: Claude (when approval needed)
**Jeremy reads**: Daily, to approve/reject

---

## The Rule

**For Jeremy**:
- Only touch files in `/JEREMY/`
- Everything is plain English
- No technical jargon
- Always up-to-date

**For AIs** (Claude, Codex, Grok):
- Read from BigQuery
- Query metadata, not files
- Update `/JEREMY/` files for Jeremy
- Everything else lives in the database

---

## Creating the Workspace

```bash
# Create Jeremy's workspace
mkdir -p "/Users/jeremyserna/Architect Library/JEREMY"

cd "/Users/jeremyserna/Architect Library/JEREMY"

# Create the 5 files
cat > 1_WHERE_ARE_WE.md << 'EOF'
# Current Status

**Updated**: 2025-10-25 2:35pm

## Where We Are
Waiting on Codex to validate baseline enrichment (VADER, KeyBERT, BERTopic).

## What's Working
- All 3 analyzers operational
- Governance logging working
- Integration tests passing

## Next Milestone
Phase 1: Add provenance fields (checksum, quality, lineage)
EOF

cat > 2_WHATS_NEXT.md << 'EOF'
# Next 3 Tasks

1. **Codex validates baseline enrichment** (today)
   - Tests VADER, KeyBERT, BERTopic working
   - Creates validation report

2. **Grok adds Phase 1 fields** (2-3 days)
   - Checksum (content hash)
   - Quality (confidence scores)
   - Lineage (provenance tracking)

3. **Start document shredding** (next week)
   - Shred 5 old docs to BigQuery
   - Test query retrieval
   - Delete originals
EOF

cat > 3_PROBLEMS.md << 'EOF'
# Current Problems

**None right now** - waiting on Codex validation

## Recently Fixed
- Too many planning docs → Created START_HERE_THE_PLAN.md
- Can't find the plan → Created /JEREMY/ workspace
- Analyzers not standardized → Grok upgraded them
EOF

cat > 4_IDEAS.md << 'EOF'
# Future Ideas

## Active (Working On)
- Shred documents to metadata (pipeline created)
- Hash-based document lifecycle
- Query BigQuery instead of reading files

## Backlog
- SMS data enrichment (after AI conversations done)
- Flash/Pro enrichment tiers
- Job search semantic queries
EOF

cat > 5_DECISIONS_NEEDED.md << 'EOF'
# Decisions Needed

**None right now** - waiting on Codex report

## Recent Decisions (Approved)
- ✅ Baseline enrichment upgrades (2025-10-25)
- ✅ Document deprecation pipeline (2025-10-25)
- ✅ /JEREMY/ workspace creation (2025-10-25)
EOF

echo "✅ Jeremy's workspace created"
```

---

## Maintenance

**Claude's job** (as planner):
- Update `1_WHERE_ARE_WE.md` after every milestone
- Update `2_WHATS_NEXT.md` after every task
- Resolve items in `3_PROBLEMS.md`
- Add to `5_DECISIONS_NEEDED.md` when approval required

**Frequency**: After every significant event (phase complete, task done, approval needed)

**Promise**: These 5 files are ALWAYS current. Jeremy never has to hunt for info.

---

## The Vision

**Before**:
- Jeremy opens `/docs/migration/Gemini/`
- Sees 30 files
- Doesn't know which to read
- Reads none, asks Claude

**After**:
- Jeremy opens `/JEREMY/`
- Sees 5 files
- Reads `1_WHERE_ARE_WE.md`
- Knows exactly where we are in 30 seconds

**For AIs**:
- Query BigQuery for historical info
- Update `/JEREMY/` for Jeremy
- Never create docs outside `/JEREMY/` (unless technical reference)

---

**Status**: Ready to create
**Timeline**: 5 minutes to set up
**Maintenance**: Claude updates after each milestone (2 min)
**Benefit**: Jeremy has his notepad, AIs drink from database
