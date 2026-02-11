---
title: "Federation Document Standard"
description: "Universal document format standard for all organisms in the federation"
version: "1.0.0"
status: "published"
last_updated: "2026-01-21"
author: "Genesis"
tags:
  - documentation
  - standard
  - federation
category: "Standards"
---

# Federation Document Standard

**The Essence** | Universal document format standard for all organisms in the federation.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Overview

This standard defines the **universal document format** that all markdown documents in the Truth Engine federation must follow. It is based on industry best practices (2025) and ensures consistency, discoverability, and maintainability across all organisms.

**Key Principles**:
- **Consistent Structure**: Every document follows the same format
- **Metadata First**: Frontmatter enables discoverability and versioning
- **Clear Hierarchy**: Predictable heading structure for navigation
- **Accessibility**: Proper formatting for tools and humans
- **Maintainability**: Standard structure simplifies updates and reviews

---

## Document Structure

### Required Elements

Every document **MUST** include:

1. **Frontmatter** (YAML metadata)
2. **Title** (H1 heading matching frontmatter title)
3. **Overview** (purpose and audience)
4. **Main Content** (sections and subsections)
5. **Related Documents** (links to related content)

### Standard Template

```markdown
---
title: "Document Title"
description: "Brief description for search and indexing"
version: "1.0.0"
status: "published"
last_updated: "2026-01-21"
author: "Organism Name"
tags:
  - tag1
  - tag2
category: "Category Name"
---

# Document Title

**The Essence** | One sentence that captures the purpose.

**Authority**: [Link to Standard] | **Status**: CANONICAL | **Last Updated**: YYYY-MM-DD

---

## Overview

A few sentences describing:
- What this document covers
- Who should read it
- When to use it

---

## Quick Reference

| Term | Definition |
|------|------------|
| Term 1 | Short definition |
| Term 2 | Short definition |

---

## [Main Section 1]

Content here.

---

## [Main Section 2]

Content here.

---

## Related Documents

- [Related Document 1](path/to/doc1.md)
- [Related Document 2](path/to/doc2.md)

---

*~{N} lines. {Purpose}. Complete.*
```

---

## Frontmatter (Metadata)

**Location**: Top of document, between `---` delimiters  
**Format**: YAML

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Document title | `"Federation Document Standard"` |
| `description` | string | Brief summary for search | `"Universal document format..."` |
| `version` | string | Document version | `"1.0.0"` |
| `status` | enum | Document status | `"draft"`, `"published"`, `"deprecated"` |
| `last_updated` | date | Last update date (YYYY-MM-DD) | `"2026-01-21"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `author` | string | Author or organism name | `"Genesis"` or `"zulip_organism"` |
| `tags` | array | Topics for discoverability | `["documentation", "standard"]` |
| `category` | string | Higher-level grouping | `"Standards"`, `"API Reference"` |
| `sidebar_label` | string | Shorter label for navigation | `"Doc Standard"` |
| `prerequisites` | array | Required knowledge/tools | `["Python 3.10+", "Basic Markdown"]` |

### Status Values

- `draft`: In progress, not ready for use
- `published`: Current, authoritative version
- `deprecated`: Superseded, migration path provided
- `archived`: Historical reference only

### Example Frontmatter

```yaml
---
title: "Federation Learning System"
description: "System for sharing learnings across organisms in the federation"
version: "1.0.0"
status: "published"
last_updated: "2026-01-21"
author: "Genesis"
tags:
  - federation
  - learning
  - knowledge-sharing
category: "Architecture"
prerequisites:
  - "Understanding of organism architecture"
  - "Basic knowledge of CloudEvents"
---
```

---

## Heading Structure

### Hierarchy Rules

| Level | Use For | Example | Max Per Doc |
|-------|---------|---------|-------------|
| `#` (H1) | Document title only | `# Document Title` | 1 |
| `##` (H2) | Major sections | `## Overview` | ~10 |
| `###` (H3) | Subsections | `### Required Fields` | ~20 |
| `####` (H4) | Rare, sub-subsections | Avoid if possible | ~5 |

### Rules

1. **Only one H1** per document (matches frontmatter title)
2. **Never skip levels**: `#` → `##` → `###` (not `#` → `###`)
3. **Consistent casing**: Use title case or sentence case consistently
4. **Descriptive headings**: Headings should be clear and scannable

### Recommended Sections

For most documents, include these sections (in order):

1. `## Overview` - Purpose and audience
2. `## Quick Reference` - Quick lookup table (if applicable)
3. `## [Main Content Sections]` - Document-specific content
4. `## Related Documents` - Links to related content
5. `## Changelog` - Version history (optional, for standards)

---

## Formatting Standards

### Text Styling

| Style | Syntax | When to Use |
|-------|--------|-------------|
| **Bold** | `**text**` | Key terms, emphasis, section headers |
| *Italic* | `*text*` | Definitions, asides, emphasis |
| `Code` | `` `code` `` | File names, commands, variables, inline code |
| ~~Strikethrough~~ | `~~text~~` | Deprecated content |

**Rule**: Use emphasis sparingly. If everything is emphasized, nothing stands out.

### Code Blocks

**Always specify language** for syntax highlighting:

````markdown
```python
def example():
    return True
```
````

**Supported languages**: `python`, `bash`, `yaml`, `json`, `markdown`, `sql`, etc.

### Lists

**Unordered** (use `-` consistently):
```markdown
- First item
- Second item
- Third item
```

**Ordered** (use real numbering):
```markdown
1. First step
2. Second step
3. Third step
```

**Nested** (2-4 spaces indentation):
```markdown
- Parent item
  - Child item
  - Another child
```

### Tables

**Use for structured/comparative data**:

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

**Alignment** (optional):
```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| Text | Text   | Text  |
```

### Links

**Internal links** (relative paths):
```markdown
[Link Text](path/to/document.md)
```

**External links**:
```markdown
[Link Text](https://example.com)
```

**Anchor links**:
```markdown
[Section Name](#section-name)
```

---

## Callouts and Indicators

### Standard Callouts

Use blockquotes with bold prefixes for callouts:

```markdown
> **NOTE**: Additional context or helpful information.

> **TIP**: Suggestions for better practices or shortcuts.

> **WARNING**: Potential issues or cautions.

> **ERROR**: Critical errors or failures.

> **IMPORTANT**: Critical information that must not be ignored.

> **CAUTION**: Dangerous operations or risks.
```

### Status Indicators

Use badges or indicators for document status:

```markdown
**Status**: `draft` | `published` | `deprecated` | `archived`

**Version**: `1.0.0`

**Last Updated**: `2026-01-21`
```

### Deprecation Notices

For deprecated documents:

```markdown
> ⚠️ **DEPRECATED** — This document is superseded by [NEW_DOC.md](path/to/NEW_DOC.md).
>
> | Status | Deprecated |
> |--------|------------|
> | Superseded By | [NEW_DOC.md](path/to/NEW_DOC.md) |
> | Deprecated Date | 2026-01-21 |
> | Reason | Brief explanation |
```

---

## Document Types

### Standards

**Purpose**: Authoritative operational standards

**Required Sections**:
- Overview
- Quick Reference (if applicable)
- The Standard / Requirements
- Examples (correct/incorrect)
- Enforcement
- Related Documents

**Example**: `FEDERATION_DOCUMENT_STANDARD.md`

### Specifications

**Purpose**: Formal technical specifications

**Required Sections**:
- Overview
- Purpose
- Specification Details
- Examples
- Version History

**Frontmatter**:
```yaml
---
title: "API Specification"
description: "Formal specification for API endpoints"
version: "1.0.0"
status: "published"
specification_type: "API"
---
```

### Architecture Documents

**Purpose**: System designs and architecture

**Required Sections**:
- Overview
- Architecture Overview
- Components
- Data Flow
- Integration Points
- Related Documents

### Guides / Tutorials

**Purpose**: Step-by-step instructions

**Required Sections**:
- Overview
- What You'll Learn
- Prerequisites
- Steps / Instructions
- Examples
- Troubleshooting
- Related Documents

### API References

**Purpose**: API endpoint documentation

**Required Sections**:
- Overview
- Authentication
- Endpoints (organized by resource)
- Request/Response Examples
- Error Codes
- Related Documents

---

## Integration with Folder Structure

This standard integrates with the **FEDERATION_FOLDER_STRUCTURE** standard:

### Document Locations

| Document Type | Location |
|---------------|----------|
| Standards | `docs/standards/` or `framework/standards/` |
| Specifications | `docs/specifications/` or `framework/patterns/` |
| Architecture | `docs/architecture/` |
| Guides | `docs/{feature}/` or `docs/guides/` |
| API Reference | `docs/api/` or `docs/{service}/api/` |

### Naming Conventions

- **Files**: `UPPER_SNAKE_CASE.md` for standards, `Title_Case.md` for guides
- **Folders**: `snake_case` matching the folder structure standard

---

## Validation Rules

### Required Checks

1. **Frontmatter Present**: YAML frontmatter between `---` delimiters
2. **Required Fields**: `title`, `description`, `version`, `status`, `last_updated`
3. **Title Match**: H1 title matches frontmatter `title`
4. **Heading Hierarchy**: No skipped levels, only one H1
5. **Overview Section**: `## Overview` section present
6. **Related Documents**: `## Related Documents` section present

### Recommended Checks

1. **Code Blocks**: Language specified for all code blocks
2. **Links**: Internal links valid (file exists)
3. **Tables**: Properly formatted (columns align)
4. **Lists**: Consistent formatting (same marker)
5. **Line Length**: Lines ≤ 100 characters (where possible)

### Enforcement

- **Pre-commit**: Automated validation via hooks
- **Pre-deployment**: Genesis validates documents before deployment
- **Runtime**: Optional document validation in organisms

---

## Anti-Patterns

### ❌ Don't Do This

```markdown
❌ WRONG: Multiple H1 titles
# Title One
# Title Two

❌ WRONG: Skipped heading levels
# Title
### Subsection (skipped ##)

❌ WRONG: No structure
Just paragraphs with no headers or sections...

❌ WRONG: Over-formatting
**Everything** is *emphasized* and `code` making nothing stand out.

❌ WRONG: Missing frontmatter
# Document Title
(no metadata)
```

### ✅ Do This

```markdown
---
title: "Document Title"
description: "Brief description"
version: "1.0.0"
status: "published"
last_updated: "2026-01-21"
---

# Document Title

**The Essence** | One sentence purpose.

---

## Overview

Clear purpose and audience.

---

## Main Content

Well-structured sections.

---
```

---

## Examples

### Standard Document

See: `framework/standards/FEDERATION_FOLDER_STRUCTURE.md`

### Specification Document

See: `framework/standards/PRIMITIVE_PATTERN_SPECIFICATION.md`

### Guide Document

See: `docs/federation_learning/07_INTEGRATION_GUIDE.md`

---

## Propagation

### Template-Based

Organism templates include document templates:
- `Primitive/seed/templates/{organism}/docs/` includes example documents
- New organisms inherit document standards

### Validation

- Pre-deployment: Genesis validates documents
- Runtime: Organisms validate their own documents
- Non-compliance: Warnings logged, deployment allowed (unless critical)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-21 | Initial standard based on industry research |

---

## Related Documents

- [FEDERATION_FOLDER_STRUCTURE.md](FEDERATION_FOLDER_STRUCTURE.md) - Folder organization
- [DOCUMENT_FORMAT.md](DOCUMENT_FORMAT.md) - Genesis-specific format (superseded)
- [NAMING_CONVENTION.md](NAMING_CONVENTION.md) - Naming standards
- [DEPRECATION.md](DEPRECATION.md) - How to deprecate documents

---

## The Principle

> **Consistent structure enables understanding. Metadata enables discovery. Standards enable federation.**

Every document in the federation follows this standard. No exceptions.

---

## Related Documents

- [FEDERATION_FOLDER_STRUCTURE.md](FEDERATION_FOLDER_STRUCTURE.md) - Folder organization standard
- [DOCUMENT_FORMAT.md](DOCUMENT_FORMAT.md) - Genesis-specific format (superseded)
- [NAMING_CONVENTION.md](NAMING_CONVENTION.md) - Naming standards
- [DEPRECATION.md](DEPRECATION.md) - How to deprecate documents
- [DOCUMENT_COMPLIANCE_SYSTEM.md](../../docs/federation_learning/DOCUMENT_COMPLIANCE_SYSTEM.md) - Compliance enforcement

---

*~400 lines. Federation document standard. Complete.*
