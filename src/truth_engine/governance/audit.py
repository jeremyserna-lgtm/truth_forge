"""
Zero Trust Audit Logging System
Truth Engine / Truth Forge

Every AI decision is logged, verified, and auditable.
No invisible decisions.
"""

import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DecisionType(Enum):
    """Types of AI decisions that get logged."""

    GENERATION = "generation"  # Text generation
    VERIFICATION = "verification"  # Claim verification
    CRITIQUE = "critique"  # Constitutional critique
    ROUTING = "routing"  # Flash/Pro routing decision
    PAYMENT = "payment"  # x402 payment transaction
    CREDENTIAL = "credential"  # Credential issuance/verification
    FRACTURE = "fracture"  # Fracture protocol trigger
    AUTHORIZATION = "authorization"  # Access control decision


class VerificationStatus(Enum):
    """Status of output verification."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"


@dataclass
class ShapingForce:
    """A force that shaped an AI decision (Fidelity Inspector data)."""

    type: str  # source, assumption, constraint, principle
    name: str  # Identifier
    description: str  # Human-readable explanation
    weight: float = 1.0  # Relative influence (0-1)


@dataclass
class AuditRecord:
    """
    Complete audit record for a single AI decision.

    This is the core data structure for Zero Trust logging.
    """

    # Identity
    audit_id: str
    timestamp: str

    # Context
    decision_type: str
    session_id: str | None = None
    user_id: str | None = None
    worker_id: str | None = None  # For NOT-ME workers

    # Input/Output
    input_hash: str = ""  # SHA-256 of input (for privacy)
    input_summary: str = ""  # Brief description
    output_hash: str = ""  # SHA-256 of output
    output_summary: str = ""  # Brief description

    # Model info
    model_used: str = ""
    model_version: str = ""
    routing_reason: str = ""  # Why this model was chosen

    # Verification
    verification_status: str = VerificationStatus.PENDING.value
    verification_score: float = 0.0
    verifications: list[dict] = field(default_factory=list)

    # Constitutional AI
    constitutional_score: float = 0.0
    principles_checked: list[str] = field(default_factory=list)
    principles_violated: list[str] = field(default_factory=list)

    # Fidelity Inspector
    shaping_forces: list[dict] = field(default_factory=list)
    reasoning_trace: str = ""

    # Fracture Protocol
    fracture_triggered: bool = False
    fracture_reason: str = ""

    # Economics
    cost_usd: float = 0.0
    payment_tx_hash: str = ""  # x402 transaction hash

    # Metadata
    duration_ms: int = 0
    error: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict) -> "AuditRecord":
        """Create from dictionary."""
        return cls(**data)


class AuditLogger:
    """
    Zero Trust audit logging system.

    Logs every AI decision to BigQuery (production) or local file (development).
    """

    def __init__(
        self,
        project_id: str = None,
        dataset: str = "spine",
        table: str = "audit_log",
        local_path: str = None,
    ):
        """
        Initialize audit logger.

        Args:
            project_id: GCP project ID (if None, uses local file)
            dataset: BigQuery dataset name
            table: BigQuery table name
            local_path: Path for local file logging (development)
        """
        self.project_id = project_id
        self.dataset = dataset
        self.table = table
        self.local_path = local_path or "logs/audit.jsonl"

        self._bq_client = None
        if project_id:
            self._init_bigquery()

    def _init_bigquery(self):
        """Initialize BigQuery client."""
        try:
            from google.cloud import bigquery

            self._bq_client = bigquery.Client(project=self.project_id)
        except ImportError:
            print("Warning: google-cloud-bigquery not installed. Using local logging.")
            self._bq_client = None

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        return str(uuid.uuid4())

    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def create_record(
        self, decision_type: DecisionType, input_data: Any = None, output_data: Any = None, **kwargs
    ) -> AuditRecord:
        """
        Create a new audit record.

        Args:
            decision_type: Type of decision being logged
            input_data: The input to the AI system
            output_data: The output from the AI system
            **kwargs: Additional audit record fields

        Returns:
            AuditRecord ready to be logged
        """
        # Prepare input/output info
        input_str = json.dumps(input_data) if input_data else ""
        output_str = json.dumps(output_data) if output_data else ""

        input_hash = self._hash_content(input_str) if input_str else ""
        output_hash = self._hash_content(output_str) if output_str else ""

        # Create summary (first 100 chars)
        input_summary = str(input_data)[:100] if input_data else ""
        output_summary = str(output_data)[:100] if output_data else ""

        return AuditRecord(
            audit_id=self._generate_audit_id(),
            timestamp=datetime.utcnow().isoformat(),
            decision_type=decision_type.value,
            input_hash=input_hash,
            input_summary=input_summary,
            output_hash=output_hash,
            output_summary=output_summary,
            **kwargs,
        )

    def log(self, record: AuditRecord) -> str:
        """
        Log an audit record.

        Returns the audit_id for reference.
        """
        if self._bq_client:
            return self._log_to_bigquery(record)
        else:
            return self._log_to_file(record)

    def _log_to_bigquery(self, record: AuditRecord) -> str:
        """Log to BigQuery."""
        table_ref = f"{self.project_id}.{self.dataset}.{self.table}"

        errors = self._bq_client.insert_rows_json(table_ref, [record.to_dict()])

        if errors:
            raise RuntimeError(f"BigQuery insert failed: {errors}")

        return record.audit_id

    def _log_to_file(self, record: AuditRecord) -> str:
        """Log to local JSONL file."""
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)

        with open(self.local_path, "a") as f:
            f.write(record.to_json() + "\n")

        return record.audit_id

    def query_by_session(self, session_id: str, limit: int = 100) -> list[AuditRecord]:
        """Query audit records by session ID."""
        if self._bq_client:
            return self._query_bigquery(f"session_id = '{session_id}'", limit)
        else:
            return self._query_local(lambda r: r.get("session_id") == session_id, limit)

    def query_by_worker(self, worker_id: str, limit: int = 100) -> list[AuditRecord]:
        """Query audit records by worker ID."""
        if self._bq_client:
            return self._query_bigquery(f"worker_id = '{worker_id}'", limit)
        else:
            return self._query_local(lambda r: r.get("worker_id") == worker_id, limit)

    def query_violations(self, limit: int = 100) -> list[AuditRecord]:
        """Query records with constitutional violations."""
        if self._bq_client:
            return self._query_bigquery("ARRAY_LENGTH(principles_violated) > 0", limit)
        else:
            return self._query_local(lambda r: len(r.get("principles_violated", [])) > 0, limit)

    def query_fractures(self, limit: int = 100) -> list[AuditRecord]:
        """Query records where Fracture Protocol was triggered."""
        if self._bq_client:
            return self._query_bigquery("fracture_triggered = TRUE", limit)
        else:
            return self._query_local(lambda r: r.get("fracture_triggered", False), limit)

    def _query_bigquery(self, where_clause: str, limit: int) -> list[AuditRecord]:
        """Execute BigQuery query."""
        query = f"""
        SELECT * FROM `{self.project_id}.{self.dataset}.{self.table}`
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        results = self._bq_client.query(query)
        return [AuditRecord.from_dict(dict(row)) for row in results]

    def _query_local(self, filter_fn, limit: int) -> list[AuditRecord]:
        """Query local file."""
        records = []
        try:
            with open(self.local_path) as f:
                for line in f:
                    record = json.loads(line)
                    if filter_fn(record):
                        records.append(AuditRecord.from_dict(record))
                        if len(records) >= limit:
                            break
        except FileNotFoundError:
            pass
        return records


class AuditContext:
    """
    Context manager for audit logging.

    Automatically captures timing and handles errors.
    """

    def __init__(
        self, logger: AuditLogger, decision_type: DecisionType, input_data: Any = None, **kwargs
    ):
        self.logger = logger
        self.decision_type = decision_type
        self.input_data = input_data
        self.kwargs = kwargs
        self.record = None
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000

        if exc_type:
            self.kwargs["error"] = str(exc_val)

        self.record = self.logger.create_record(
            decision_type=self.decision_type,
            input_data=self.input_data,
            duration_ms=int(duration),
            **self.kwargs,
        )

        self.logger.log(self.record)

        # Don't suppress exceptions
        return False

    def set_output(self, output_data: Any):
        """Set the output data before context exits."""
        self.kwargs["output_data"] = output_data

    def set_verification(
        self, status: VerificationStatus, score: float, details: list[dict] = None
    ):
        """Set verification results."""
        self.kwargs["verification_status"] = status.value
        self.kwargs["verification_score"] = score
        self.kwargs["verifications"] = details or []

    def set_constitutional(self, score: float, checked: list[str], violated: list[str] = None):
        """Set constitutional evaluation results."""
        self.kwargs["constitutional_score"] = score
        self.kwargs["principles_checked"] = checked
        self.kwargs["principles_violated"] = violated or []

    def add_shaping_force(self, force_type: str, name: str, description: str, weight: float = 1.0):
        """Add a shaping force (Fidelity Inspector)."""
        if "shaping_forces" not in self.kwargs:
            self.kwargs["shaping_forces"] = []

        self.kwargs["shaping_forces"].append(
            {"type": force_type, "name": name, "description": description, "weight": weight}
        )

    def trigger_fracture(self, reason: str):
        """Mark that Fracture Protocol was triggered."""
        self.kwargs["fracture_triggered"] = True
        self.kwargs["fracture_reason"] = reason


# ═══════════════════════════════════════════════════════════════════════════════
# BIGQUERY SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

AUDIT_LOG_SCHEMA = """
-- Schema for spine.audit_log table
-- Run this in BigQuery to create the table

CREATE TABLE IF NOT EXISTS `{project}.spine.audit_log` (
  -- Identity
  audit_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  
  -- Context
  decision_type STRING NOT NULL,
  session_id STRING,
  user_id STRING,
  worker_id STRING,
  
  -- Input/Output
  input_hash STRING,
  input_summary STRING,
  output_hash STRING,
  output_summary STRING,
  
  -- Model info
  model_used STRING,
  model_version STRING,
  routing_reason STRING,
  
  -- Verification
  verification_status STRING,
  verification_score FLOAT64,
  verifications JSON,
  
  -- Constitutional AI
  constitutional_score FLOAT64,
  principles_checked ARRAY<STRING>,
  principles_violated ARRAY<STRING>,
  
  -- Fidelity Inspector
  shaping_forces JSON,
  reasoning_trace STRING,
  
  -- Fracture Protocol
  fracture_triggered BOOL DEFAULT FALSE,
  fracture_reason STRING,
  
  -- Economics
  cost_usd FLOAT64,
  payment_tx_hash STRING,
  
  -- Metadata
  duration_ms INT64,
  error STRING,
  tags ARRAY<STRING>
)
PARTITION BY DATE(timestamp)
CLUSTER BY decision_type, worker_id
OPTIONS(
  description="Zero Trust audit log for all AI decisions"
);

-- Index for fast session lookups
CREATE SEARCH INDEX IF NOT EXISTS audit_session_idx 
ON `{project}.spine.audit_log`(session_id);

-- Index for fast worker lookups
CREATE SEARCH INDEX IF NOT EXISTS audit_worker_idx 
ON `{project}.spine.audit_log`(worker_id);
"""


def get_schema_sql(project_id: str) -> str:
    """Get the BigQuery schema SQL with project ID substituted."""
    return AUDIT_LOG_SCHEMA.format(project=project_id)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Demo with local file logging
    logger = AuditLogger(local_path="logs/demo_audit.jsonl")

    # Example: Log a generation decision
    with AuditContext(
        logger,
        DecisionType.GENERATION,
        input_data={"query": "What is the capital of France?"},
        session_id="demo-session-123",
        model_used="gemini-1.5-flash",
    ) as ctx:
        # Simulate work
        ctx.add_shaping_force("source", "user_query", "Direct question about geography")
        ctx.add_shaping_force("constraint", "factual_accuracy", "Must be verifiable fact")

        ctx.set_output({"response": "The capital of France is Paris."})
        ctx.set_verification(VerificationStatus.PASSED, 0.99)
        ctx.set_constitutional(score=1.0, checked=["CRD-002", "CRD-007"], violated=[])

    print(f"Logged audit record: {ctx.record.audit_id}")
    print(f"Log file: {logger.local_path}")

    # Example: Log a fracture
    with AuditContext(
        logger,
        DecisionType.FRACTURE,
        input_data={"claim": "The earth is flat and spherical."},
        session_id="demo-session-123",
    ) as ctx:
        ctx.trigger_fracture("Self-contradictory claim detected")

    print(f"Fracture logged: {ctx.record.audit_id}")
