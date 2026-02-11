#!/usr/bin/env python3
"""Document Index Generator.

Scans all markdown documents, extracts frontmatter, builds relationship graph,
generates index files, and validates the document ecosystem.

Usage:
    python scripts/document_index.py                    # Full scan and report
    python scripts/document_index.py --validate        # Validation only
    python scripts/document_index.py --graph           # Generate graph JSON
    python scripts/document_index.py --obsidian        # Generate Obsidian index note
    python scripts/document_index.py --add-frontmatter # Add missing frontmatter

MOLT LINEAGE:
- Source: New creation for document management
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Document type taxonomy
DOCUMENT_TYPES = {
    "framework",
    "standard",
    "specification",
    "plan",
    "adr",
    "guide",
    "reference",
    "index",
    "log",
    "personal",
}

# Status lifecycle
STATUS_LIFECYCLE = {
    "draft",
    "review",
    "canonical",
    "deprecated",
    "archived",
}

# Domain taxonomy
DOMAINS = {
    "framework",
    "not-me",
    "primitive-engine",
    "credential-atlas",
    "infrastructure",
    "business",
    "personal",
    "operations",
}

# Directories to scan
SCAN_DIRECTORIES = [
    "docs",
    "framework",
    ".agent",
]

# Directories to skip
SKIP_DIRECTORIES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".obsidian",
    "archive",
}


@dataclass
class Document:
    """Parsed document with frontmatter and metadata."""

    path: Path
    frontmatter: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    wikilinks: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        """Document ID from frontmatter or filename."""
        return self.frontmatter.get("id", self.path.stem)

    @property
    def title(self) -> str:
        """Document title."""
        return self.frontmatter.get("title", self.path.stem.replace("_", " ").title())

    @property
    def doc_type(self) -> str:
        """Document type."""
        return self.frontmatter.get("type", "unknown")

    @property
    def status(self) -> str:
        """Document status."""
        return self.frontmatter.get("status", "unknown")

    @property
    def domain(self) -> str:
        """Document domain."""
        return self.frontmatter.get("domain", "unknown")

    @property
    def related(self) -> list[str]:
        """Related document IDs."""
        return self.frontmatter.get("related", [])

    @property
    def supersedes(self) -> list[str]:
        """Documents this supersedes."""
        return self.frontmatter.get("supersedes", [])

    @property
    def blocks(self) -> list[str]:
        """Prerequisite documents."""
        return self.frontmatter.get("blocks", [])

    @property
    def implements(self) -> list[str]:
        """Standards/ADRs implemented."""
        return self.frontmatter.get("implements", [])

    @property
    def tags(self) -> list[str]:
        """Searchable tags."""
        return self.frontmatter.get("tags", [])

    @property
    def has_frontmatter(self) -> bool:
        """Check if document has any frontmatter."""
        return bool(self.frontmatter)


@dataclass
class ValidationResult:
    """Result of document validation."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0


@dataclass
class IndexReport:
    """Full index report."""

    documents: dict[str, Document] = field(default_factory=dict)
    by_type: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    by_domain: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    by_status: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    by_tag: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    validation: ValidationResult = field(default_factory=ValidationResult)
    graph_edges: list[tuple[str, str, str]] = field(default_factory=list)


def parse_document(path: Path) -> Document:
    """Parse a markdown document, extracting frontmatter and wikilinks."""
    content = path.read_text(encoding="utf-8")

    frontmatter: dict[str, Any] = {}
    body = content

    # Extract frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError as e:
                logger.warning("YAML parse error in %s: %s", path, e)
            body = parts[2].strip()

    # Extract wikilinks from body
    wikilinks = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body)

    return Document(
        path=path,
        frontmatter=frontmatter,
        content=body,
        wikilinks=wikilinks,
    )


def scan_documents(root: Path) -> list[Document]:
    """Scan directory tree for markdown documents."""
    documents: list[Document] = []

    for scan_dir in SCAN_DIRECTORIES:
        dir_path = root / scan_dir
        if not dir_path.exists():
            continue

        for md_path in dir_path.rglob("*.md"):
            # Skip excluded directories
            if any(skip in md_path.parts for skip in SKIP_DIRECTORIES):
                continue

            try:
                doc = parse_document(md_path)
                documents.append(doc)
            except Exception as e:
                logger.error("Failed to parse %s: %s", md_path, e)

    return documents


def validate_document(doc: Document, all_ids: set[str]) -> ValidationResult:
    """Validate a single document."""
    result = ValidationResult()

    # Required frontmatter check
    if not doc.has_frontmatter:
        result.warnings.append(f"Missing frontmatter: {doc.path}")
        return result  # Can't validate further without frontmatter

    # Type validation
    if doc.doc_type not in DOCUMENT_TYPES and doc.doc_type != "unknown":
        result.errors.append(f"Invalid type '{doc.doc_type}': {doc.path}")

    # Status validation
    if doc.status not in STATUS_LIFECYCLE and doc.status != "unknown":
        result.errors.append(f"Invalid status '{doc.status}': {doc.path}")

    # Domain validation
    if doc.domain not in DOMAINS and doc.domain != "unknown":
        result.warnings.append(f"Unknown domain '{doc.domain}': {doc.path}")

    # Relationship validation
    for rel_id in doc.related:
        if rel_id not in all_ids:
            result.warnings.append(f"Related doc '{rel_id}' not found: {doc.path}")

    for sup_id in doc.supersedes:
        if sup_id not in all_ids:
            result.warnings.append(f"Superseded doc '{sup_id}' not found: {doc.path}")

    for block_id in doc.blocks:
        if block_id not in all_ids:
            result.warnings.append(f"Blocking doc '{block_id}' not found: {doc.path}")

    return result


def build_index(documents: list[Document]) -> IndexReport:
    """Build full index report from documents."""
    report = IndexReport()

    # Index by ID
    for doc in documents:
        report.documents[doc.id] = doc
        report.by_type[doc.doc_type].append(doc.id)
        report.by_domain[doc.domain].append(doc.id)
        report.by_status[doc.status].append(doc.id)
        for tag in doc.tags:
            report.by_tag[tag].append(doc.id)

    # Build graph edges
    for doc in documents:
        for rel_id in doc.related:
            report.graph_edges.append((doc.id, rel_id, "related"))
        for sup_id in doc.supersedes:
            report.graph_edges.append((doc.id, sup_id, "supersedes"))
        for block_id in doc.blocks:
            report.graph_edges.append((doc.id, block_id, "blocks"))
        for impl_id in doc.implements:
            report.graph_edges.append((doc.id, impl_id, "implements"))
        for wikilink in doc.wikilinks:
            report.graph_edges.append((doc.id, wikilink, "links"))

    # Validate all documents
    all_ids = set(report.documents.keys())
    for doc in documents:
        result = validate_document(doc, all_ids)
        report.validation.errors.extend(result.errors)
        report.validation.warnings.extend(result.warnings)

    # Check for orphan relationships (one-directional when should be bidirectional)
    related_pairs: set[frozenset[str]] = set()
    for doc in documents:
        for rel_id in doc.related:
            related_pairs.add(frozenset([doc.id, rel_id]))

    for doc in documents:
        for rel_id in doc.related:
            if rel_id in report.documents:
                other_doc = report.documents[rel_id]
                if doc.id not in other_doc.related:
                    report.validation.warnings.append(
                        f"One-directional relationship: {doc.id} → {rel_id} "
                        f"(consider adding {doc.id} to {rel_id}'s related)"
                    )

    return report


def generate_summary(report: IndexReport) -> str:
    """Generate human-readable summary."""
    lines = [
        "# Document Index Report",
        "",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Total Documents**: {len(report.documents)}",
        "",
        "## By Type",
        "",
    ]

    for doc_type in sorted(report.by_type.keys()):
        count = len(report.by_type[doc_type])
        lines.append(f"- **{doc_type}**: {count}")

    lines.extend(["", "## By Domain", ""])

    for domain in sorted(report.by_domain.keys()):
        count = len(report.by_domain[domain])
        lines.append(f"- **{domain}**: {count}")

    lines.extend(["", "## By Status", ""])

    for status in sorted(report.by_status.keys()):
        count = len(report.by_status[status])
        lines.append(f"- **{status}**: {count}")

    lines.extend(["", "## Validation", ""])

    if report.validation.errors:
        lines.append(f"**Errors**: {len(report.validation.errors)}")
        for error in report.validation.errors[:10]:
            lines.append(f"- ❌ {error}")
        if len(report.validation.errors) > 10:
            lines.append(f"- ... and {len(report.validation.errors) - 10} more")
    else:
        lines.append("**Errors**: 0 ✅")

    lines.append("")

    if report.validation.warnings:
        lines.append(f"**Warnings**: {len(report.validation.warnings)}")
        for warning in report.validation.warnings[:10]:
            lines.append(f"- ⚠️ {warning}")
        if len(report.validation.warnings) > 10:
            lines.append(f"- ... and {len(report.validation.warnings) - 10} more")
    else:
        lines.append("**Warnings**: 0 ✅")

    lines.extend(["", "## Graph Statistics", ""])
    lines.append(f"**Nodes**: {len(report.documents)}")
    lines.append(f"**Edges**: {len(report.graph_edges)}")

    return "\n".join(lines)


def generate_graph_json(report: IndexReport) -> dict[str, Any]:
    """Generate graph data for visualization."""
    nodes = []
    for doc_id, doc in report.documents.items():
        nodes.append(
            {
                "id": doc_id,
                "title": doc.title,
                "type": doc.doc_type,
                "status": doc.status,
                "domain": doc.domain,
                "path": str(doc.path),
                "tags": doc.tags,
            }
        )

    edges = []
    for source, target, rel_type in report.graph_edges:
        edges.append(
            {
                "source": source,
                "target": target,
                "type": rel_type,
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "generated": datetime.now().isoformat(),
    }


def generate_obsidian_index(report: IndexReport, root: Path) -> str:
    """Generate Obsidian-compatible index note with Dataview queries."""
    lines = [
        "---",
        "id: DOCUMENT_INDEX",
        "title: Document Index",
        "type: index",
        "status: canonical",
        "domain: infrastructure",
        f"created: {date.today().isoformat()}",
        f"updated: {date.today().isoformat()}",
        "author: system",
        "cssclass: index",
        "publish: true",
        "---",
        "",
        "# Document Index",
        "",
        "**Auto-generated document index. Do not edit manually.**",
        "",
        "## Statistics",
        "",
        f"- **Total Documents**: {len(report.documents)}",
        f"- **Graph Edges**: {len(report.graph_edges)}",
        f"- **Validation Errors**: {len(report.validation.errors)}",
        f"- **Validation Warnings**: {len(report.validation.warnings)}",
        "",
        "## By Type",
        "",
        "```dataview",
        "TABLE type, status, domain",
        "FROM \"docs\" OR \"framework\"",
        "WHERE type",
        "GROUP BY type",
        "```",
        "",
        "## By Domain",
        "",
        "```dataview",
        "TABLE title, type, status",
        "FROM \"docs\" OR \"framework\"",
        "WHERE domain",
        "GROUP BY domain",
        "```",
        "",
        "## Recent Updates",
        "",
        "```dataview",
        "TABLE title, type, updated",
        "FROM \"docs\" OR \"framework\"",
        "WHERE updated",
        "SORT updated DESC",
        "LIMIT 20",
        "```",
        "",
        "## Documents Needing Review",
        "",
        "```dataview",
        "TABLE title, status, last_reviewed",
        "FROM \"docs\" OR \"framework\"",
        'WHERE status = "draft" OR status = "review"',
        "SORT updated DESC",
        "```",
        "",
        "## Deprecated Documents",
        "",
        "```dataview",
        "TABLE title, superseded_by",
        "FROM \"docs\" OR \"framework\"",
        'WHERE status = "deprecated"',
        "```",
        "",
        "## All Documents",
        "",
    ]

    # Add flat list for non-Dataview users
    for doc_type in sorted(report.by_type.keys()):
        lines.append(f"### {doc_type.title()}")
        lines.append("")
        for doc_id in sorted(report.by_type[doc_type]):
            doc = report.documents[doc_id]
            rel_path = doc.path.relative_to(root)
            lines.append(f"- [[{doc_id}|{doc.title}]] ({doc.status})")
        lines.append("")

    return "\n".join(lines)


def generate_frontmatter_template(path: Path) -> str:
    """Generate frontmatter template for a document without one."""
    # Infer type from path
    doc_type = "unknown"
    if "framework" in path.parts:
        if path.name.startswith("STANDARD_"):
            doc_type = "standard"
        elif path.name.endswith("INDEX.md"):
            doc_type = "index"
        else:
            doc_type = "framework"
    elif "plans" in path.parts:
        doc_type = "plan"
    elif "technical" in path.parts:
        doc_type = "specification"
    elif "decisions" in path.parts:
        doc_type = "adr"
    elif "personal" in path.parts:
        doc_type = "personal"

    # Infer domain from path
    domain = "unknown"
    if "framework" in path.parts:
        domain = "framework"
    elif "not_me" in str(path).lower() or "not-me" in str(path).lower():
        domain = "not-me"
    elif "primitive" in str(path).lower():
        domain = "primitive-engine"
    elif "credential" in str(path).lower():
        domain = "credential-atlas"
    elif "business" in path.parts:
        domain = "business"
    elif "personal" in path.parts:
        domain = "personal"
    elif "technical" in path.parts:
        domain = "infrastructure"

    doc_id = path.stem

    return f"""---
id: {doc_id}
title: "{doc_id.replace('_', ' ').title()}"
type: {doc_type}
status: draft
domain: {domain}
created: {date.today().isoformat()}
updated: {date.today().isoformat()}
author: jeremy
related: []
tags: []
---

"""


def add_missing_frontmatter(documents: list[Document], root: Path, dry_run: bool = True) -> int:
    """Add frontmatter to documents missing it."""
    count = 0

    for doc in documents:
        if doc.has_frontmatter:
            continue

        template = generate_frontmatter_template(doc.path)
        new_content = template + doc.content

        if dry_run:
            logger.info("Would add frontmatter to: %s", doc.path)
        else:
            doc.path.write_text(new_content, encoding="utf-8")
            logger.info("Added frontmatter to: %s", doc.path)

        count += 1

    return count


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Document Index Generator")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validation only (no output files)",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Generate graph JSON",
    )
    parser.add_argument(
        "--obsidian",
        action="store_true",
        help="Generate Obsidian index note",
    )
    parser.add_argument(
        "--add-frontmatter",
        action="store_true",
        help="Add missing frontmatter to documents",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't write files)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )

    args = parser.parse_args()

    # Ensure we're in the right directory
    root = args.root
    if not (root / "framework").exists():
        logger.error("Not in truth_forge root (framework/ not found)")
        return 1

    logger.info("Scanning documents in %s...", root)
    documents = scan_documents(root)
    logger.info("Found %d documents", len(documents))

    # Build index
    report = build_index(documents)

    # Generate summary
    summary = generate_summary(report)
    print(summary)

    # Handle specific modes
    if args.add_frontmatter:
        count = add_missing_frontmatter(documents, root, dry_run=args.dry_run)
        logger.info("Documents needing frontmatter: %d", count)

    if args.graph:
        graph_data = generate_graph_json(report)
        output_path = root / "data" / "document_graph.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not args.dry_run:
            output_path.write_text(json.dumps(graph_data, indent=2))
            logger.info("Graph written to: %s", output_path)
        else:
            logger.info("Would write graph to: %s", output_path)

    if args.obsidian:
        obsidian_index = generate_obsidian_index(report, root)
        output_path = root / "docs" / "DOCUMENT_INDEX.md"
        if not args.dry_run:
            output_path.write_text(obsidian_index)
            logger.info("Obsidian index written to: %s", output_path)
        else:
            logger.info("Would write Obsidian index to: %s", output_path)

    # Return exit code based on validation
    if report.validation.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
