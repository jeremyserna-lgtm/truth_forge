"""Stage 0: Assessment - Analyze raw data structure.

PATTERN: HOLD1 (raw files) → AGENT (analysis) → HOLD2 (report)

This stage scans the raw JSONL files to generate a comprehensive assessment
report without persisting any processed data. It provides:
- File counts and sizes
- Message counts by role
- Date range coverage
- Schema validation
- Quality metrics

Usage:
    stage = AssessmentStage(config)
    result = stage.run()
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from pipelines.core.stage import Stage


logger = logging.getLogger(__name__)


class AssessmentStage(Stage):
    """Stage 0: Assess raw data structure and quality."""

    STAGE_TYPE = "assessment"

    def __init__(self, config: Any) -> None:
        """Initialize assessment stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.stats: dict[str, Any] = {
            "files": [],
            "total_files": 0,
            "total_messages": 0,
            "total_size_bytes": 0,
            "messages_by_role": Counter(),
            "messages_by_type": Counter(),
            "date_range": {"earliest": None, "latest": None},
            "schema_issues": [],
            "quality_metrics": {},
        }

    def read_input(self) -> list[dict[str, Any]]:
        """Scan source directory for JSONL files.
        
        Returns:
            List of file metadata dictionaries.
        """
        source_path = self.config.extra.get("source_path", "~/.claude-code/sessions")
        source_dir = Path(source_path).expanduser()
        
        if not source_dir.exists():
            logger.warning(f"Source directory does not exist: {source_dir}")
            return []
        
        files = []
        for jsonl_file in source_dir.glob("*.jsonl"):
            file_stat = jsonl_file.stat()
            files.append({
                "path": str(jsonl_file),
                "size_bytes": file_stat.st_size,
                "modified_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            })
            logger.debug(f"Found file: {jsonl_file.name} ({file_stat.st_size} bytes)")
        
        self.stats["total_files"] = len(files)
        self.stats["files"] = files
        
        return files

    def transform(self, file_record: dict[str, Any]) -> dict[str, Any] | None:
        """Analyze a single JSONL file.
        
        Args:
            file_record: File metadata.
            
        Returns:
            Analysis results for the file.
        """
        file_path = Path(file_record["path"])
        
        file_stats = {
            "path": str(file_path),
            "messages": 0,
            "size_bytes": file_record["size_bytes"],
            "roles": Counter(),
            "types": Counter(),
            "schema_valid": True,
            "issues": [],
        }
        
        try:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        file_stats["messages"] += 1
                        
                        # Track role distribution
                        role = record.get("role", "unknown")
                        file_stats["roles"][role] += 1
                        self.stats["messages_by_role"][role] += 1
                        
                        # Track message type
                        msg_type = record.get("message_type", "unknown")
                        file_stats["types"][msg_type] += 1
                        self.stats["messages_by_type"][msg_type] += 1
                        
                        # Validate schema
                        required_fields = ["session_id", "message_index", "text", "role"]
                        missing_fields = [f for f in required_fields if f not in record]
                        if missing_fields:
                            issue = f"Line {line_num}: Missing fields {missing_fields}"
                            file_stats["issues"].append(issue)
                            file_stats["schema_valid"] = False
                        
                        # Track date range
                        if "timestamp_utc" in record:
                            ts = record["timestamp_utc"]
                            if self.stats["date_range"]["earliest"] is None:
                                self.stats["date_range"]["earliest"] = ts
                                self.stats["date_range"]["latest"] = ts
                            else:
                                if ts < self.stats["date_range"]["earliest"]:
                                    self.stats["date_range"]["earliest"] = ts
                                if ts > self.stats["date_range"]["latest"]:
                                    self.stats["date_range"]["latest"] = ts
                    
                    except json.JSONDecodeError as e:
                        issue = f"Line {line_num}: JSON parse error: {e}"
                        file_stats["issues"].append(issue)
                        file_stats["schema_valid"] = False
            
            self.stats["total_messages"] += file_stats["messages"]
            self.stats["total_size_bytes"] += file_stats["size_bytes"]
            
            if file_stats["issues"]:
                self.stats["schema_issues"].extend(file_stats["issues"])
            
            return file_stats
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None

    def write_output(self, file_analyses: list[dict[str, Any]]) -> int:
        """Generate assessment report.
        
        Args:
            file_analyses: Analysis results for each file.
            
        Returns:
            Number of files analyzed.
        """
        # Calculate quality metrics
        valid_files = sum(1 for f in file_analyses if f and f["schema_valid"])
        self.stats["quality_metrics"] = {
            "valid_files": valid_files,
            "invalid_files": len(file_analyses) - valid_files,
            "schema_compliance_rate": valid_files / len(file_analyses) if file_analyses else 0,
            "avg_messages_per_file": (
                self.stats["total_messages"] / len(file_analyses) if file_analyses else 0
            ),
        }
        
        # Write report
        output_path = Path(self.config.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_path = output_path.parent / "assessment_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "total_files": self.stats["total_files"],
                        "total_messages": self.stats["total_messages"],
                        "total_size_mb": round(self.stats["total_size_bytes"] / 1024 / 1024, 2),
                        "messages_by_role": dict(self.stats["messages_by_role"]),
                        "messages_by_type": dict(self.stats["messages_by_type"]),
                        "date_range": self.stats["date_range"],
                    },
                    "quality": self.stats["quality_metrics"],
                    "schema_issues_count": len(self.stats["schema_issues"]),
                    "schema_issues": self.stats["schema_issues"][:100],  # First 100 issues
                    "files": file_analyses,
                },
                f,
                indent=2,
            )
        
        logger.info(f"Assessment report written to: {report_path}")
        logger.info(
            f"Summary: {self.stats['total_files']} files, "
            f"{self.stats['total_messages']} messages, "
            f"{round(self.stats['total_size_bytes'] / 1024 / 1024, 2)} MB"
        )
        
        return len(file_analyses)


__all__ = ["AssessmentStage"]
