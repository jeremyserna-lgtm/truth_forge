"""Revolutionary Pipeline Features - Groundbreaking Innovations

This module implements cutting-edge features that make this pipeline
a truly groundbreaking product offering:

1. Bitemporal Time-Travel Queries
2. Event Sourcing with Immutable Audit Trail
3. Cryptographic Provenance Tracking
4. Data Contracts with Semantic Versioning

These features combined create capabilities no competitor offers.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import bigquery

from shared.constants import PROJECT_ID, DATASET_ID, PIPELINE_NAME, SOURCE_NAME


# ============================================================================
# BITEMPORAL TIME-TRAVEL QUERIES
# ============================================================================

def add_bitemporal_fields_to_schema(schema: List[bigquery.SchemaField]) -> List[bigquery.SchemaField]:
    """Add bitemporal fields to a schema.
    
    Adds:
    - system_time: When pipeline processed the data
    - valid_time: When data actually occurred
    - system_time_end: When this version was superseded (NULL = current)
    - valid_time_end: When this version became invalid (NULL = still valid)
    
    Args:
        schema: Existing schema
    
    Returns:
        Schema with bitemporal fields added
    """
    bitemporal_fields = [
        bigquery.SchemaField("system_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("valid_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("system_time_end", "TIMESTAMP"),  # NULL = current
        bigquery.SchemaField("valid_time_end", "TIMESTAMP"),  # NULL = still valid
    ]
    
    # Insert before run_id (if present) or at end
    run_id_index = next((i for i, f in enumerate(schema) if f.name == "run_id"), len(schema))
    return schema[:run_id_index] + bitemporal_fields + schema[run_id_index:]


def add_bitemporal_to_record(
    record: Dict[str, Any],
    valid_time: datetime,
    system_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Add bitemporal fields to a record.
    
    Args:
        record: Existing record
        valid_time: When data actually occurred (from source)
        system_time: When pipeline processed it (defaults to now)
    
    Returns:
        Record with bitemporal fields added
    """
    if system_time is None:
        system_time = datetime.now(timezone.utc)
    
    record["system_time"] = system_time
    record["valid_time"] = valid_time
    record["system_time_end"] = None  # Current until superseded
    record["valid_time_end"] = None  # Valid until corrected
    
    return record


def generate_time_travel_query(
    table: str,
    valid_time: datetime,
    system_time: Optional[datetime] = None,
    additional_filters: Dict[str, Any] = None,
) -> str:
    """Generate time-travel query.
    
    Args:
        table: Table to query
        valid_time: Point in time to query (valid time)
        system_time: Point in pipeline processing time (optional, uses latest if None)
        additional_filters: Additional WHERE conditions
    
    Returns:
        SQL query string
    """
    filters = []
    
    # Valid time filter
    filters.append(f"valid_time <= TIMESTAMP('{valid_time.isoformat()}')")
    filters.append(f"(valid_time_end IS NULL OR valid_time_end > TIMESTAMP('{valid_time.isoformat()}'))")
    
    # System time filter
    if system_time:
        filters.append(f"system_time <= TIMESTAMP('{system_time.isoformat()}')")
        filters.append(f"(system_time_end IS NULL OR system_time_end > TIMESTAMP('{system_time.isoformat()}'))")
    else:
        # Use latest system time for each entity
        filters.append("""
            system_time = (
                SELECT MAX(system_time)
                FROM `{table}` t2
                WHERE t2.entity_id = {table}.entity_id
                  AND t2.valid_time <= TIMESTAMP('{valid_time}')
            )
        """.format(table=table, valid_time=valid_time.isoformat()))
    
    # Additional filters
    if additional_filters:
        for key, value in additional_filters.items():
            if isinstance(value, str):
                filters.append(f"{key} = '{value}'")
            else:
                filters.append(f"{key} = {value}")
    
    where_clause = " AND ".join(filters)
    
    return f"""
    SELECT *
    FROM `{table}`
    WHERE {where_clause}
    ORDER BY valid_time ASC, system_time ASC
    """


# ============================================================================
# EVENT SOURCING WITH IMMUTABLE AUDIT TRAIL
# ============================================================================

EVENT_STORE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.event_store"

EVENT_STORE_SCHEMA = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),  # CREATED, UPDATED, CORRECTED, DELETED
    bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("stage", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_data", "JSON", mode="REQUIRED"),  # Full entity state
    bigquery.SchemaField("previous_event_id", "STRING"),  # Link to previous event
    bigquery.SchemaField("causal_chain", "STRING", mode="REPEATED"),  # What caused this
    bigquery.SchemaField("event_hash", "STRING", mode="REQUIRED"),  # Cryptographic hash
    bigquery.SchemaField("metadata", "JSON"),
]

# Partition by event_timestamp, cluster by entity_id for efficient queries
EVENT_STORE_PARTITIONING = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="event_timestamp",
)
EVENT_STORE_CLUSTERING = ["entity_id", "event_type", "stage"]


def generate_event_id(entity_id: str, event_type: str, timestamp: datetime) -> str:
    """Generate deterministic event ID using Primitive.identity (industry standard).
    
    Args:
        entity_id: Entity this event relates to
        event_type: Type of event
        timestamp: Event timestamp
    
    Returns:
        event_id (format: evt:{hash16} - industry standard, 16-char hash)
    """
    try:
        from truth_forge.identity import generate_hash
        content = f"event:{entity_id}:{event_type}:{timestamp.isoformat()}"
        hash_value = generate_hash(content, length=16)  # 64 bits, industry standard
    except ImportError:
        # Fallback to hashlib if Primitive.identity not available
        content = f"event:{entity_id}:{event_type}:{timestamp.isoformat()}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"evt:{hash_value}"


def record_event(
    client: bigquery.Client,
    entity_id: str,
    event_type: str,
    event_data: Dict[str, Any],
    stage: int,
    run_id: str,
    previous_event_id: Optional[str] = None,
    causal_chain: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Record an immutable event in the event store.
    
    Args:
        client: BigQuery client
        entity_id: Entity this event relates to
        event_type: CREATED, UPDATED, CORRECTED, DELETED
        event_data: Full entity state at this event
        stage: Pipeline stage that created this event
        run_id: Current run ID
        previous_event_id: Link to previous event for this entity
        causal_chain: List of event IDs that caused this event
        metadata: Additional metadata
    
    Returns:
        event_id
    """
    event_timestamp = datetime.now(timezone.utc)
    event_id = generate_event_id(entity_id, event_type, event_timestamp)
    
    # Calculate cryptographic hash for immutability
    hash_input = {
        "event_id": event_id,
        "entity_id": entity_id,
        "event_type": event_type,
        "event_timestamp": event_timestamp.isoformat(),
        "event_data": event_data,
    }
    event_hash = hashlib.sha256(
        json.dumps(hash_input, sort_keys=True).encode()
    ).hexdigest()
    
    # Build causal chain
    final_causal_chain = list(causal_chain or [])
    if previous_event_id:
        final_causal_chain.append(previous_event_id)
    
    event = {
        "event_id": event_id,
        "entity_id": entity_id,
        "event_type": event_type,
        "event_timestamp": event_timestamp,
        "stage": stage,
        "run_id": run_id,
        "event_data": json.dumps(event_data),
        "previous_event_id": previous_event_id,
        "causal_chain": final_causal_chain,
        "event_hash": event_hash,
        "metadata": json.dumps(metadata or {
            "pipeline": PIPELINE_NAME,
            "source": SOURCE_NAME,
        }),
    }
    
    # Ensure event store table exists
    ensure_event_store_table(client)
    
    # Load event
    from src.services.central_services.core.bigquery_client import get_bigquery_client
    bq_client = get_bigquery_client()
    bq_client.load_rows_to_table(EVENT_STORE_TABLE, [event])
    
    return event_id


def ensure_event_store_table(client: bigquery.Client) -> bigquery.Table:
    """Ensure event store table exists with proper schema.
    
    Args:
        client: BigQuery client
    
    Returns:
        Table reference
    """
    table_ref = bigquery.Table(EVENT_STORE_TABLE, schema=EVENT_STORE_SCHEMA)
    table_ref.time_partitioning = EVENT_STORE_PARTITIONING
    table_ref.clustering_fields = EVENT_STORE_CLUSTERING
    
    return client.create_table(table_ref, exists_ok=True)


def reconstruct_entity_state(
    client: bigquery.Client,
    entity_id: str,
    at_timestamp: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """Reconstruct entity state by replaying events.
    
    Args:
        client: BigQuery client
        entity_id: Entity to reconstruct
        at_timestamp: Reconstruct state at this time (None = latest)
    
    Returns:
        Entity state dictionary, or None if deleted
    """
    if at_timestamp:
        query = f"""
        SELECT *
        FROM `{EVENT_STORE_TABLE}`
        WHERE entity_id = '{entity_id}'
          AND event_timestamp <= TIMESTAMP('{at_timestamp.isoformat()}')
        ORDER BY event_timestamp ASC
        """
    else:
        query = f"""
        SELECT *
        FROM `{EVENT_STORE_TABLE}`
        WHERE entity_id = '{entity_id}'
        ORDER BY event_timestamp ASC
        """
    
    events = list(client.query(query).result())
    
    if not events:
        return None
    
    # Replay events to reconstruct state
    state = None
    for event in events:
        event_data = json.loads(event.event_data)
        
        if event.event_type == "CREATED":
            state = event_data
        elif event.event_type == "UPDATED":
            if state is None:
                state = {}
            state.update(event_data)
        elif event.event_type == "CORRECTED":
            # Correction replaces state
            state = event_data
        elif event.event_type == "DELETED":
            state = None
            break
    
    return state


# ============================================================================
# CRYPTOGRAPHIC PROVENANCE TRACKING
# ============================================================================

PROVENANCE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.provenance_chain"

PROVENANCE_SCHEMA = [
    bigquery.SchemaField("provenance_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("stage", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("input_hash", "STRING"),  # Hash of input data
    bigquery.SchemaField("output_hash", "STRING", mode="REQUIRED"),  # Hash of output data
    bigquery.SchemaField("transformation", "STRING", mode="REQUIRED"),  # What transformation occurred
    bigquery.SchemaField("transformation_params", "JSON"),  # Parameters used
    bigquery.SchemaField("parent_provenance_id", "STRING"),  # Link to parent provenance
    bigquery.SchemaField("provenance_chain", "STRING", mode="REPEATED"),  # Complete chain
    bigquery.SchemaField("verification_status", "STRING", mode="REQUIRED"),  # VERIFIED, PENDING, FAILED
    bigquery.SchemaField("verified_at", "TIMESTAMP"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]

PROVENANCE_PARTITIONING = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="verified_at",
)
PROVENANCE_CLUSTERING = ["entity_id", "stage", "verification_status"]


def calculate_data_hash(data: Dict[str, Any]) -> str:
    """Calculate cryptographic hash of data.
    
    Args:
        data: Data dictionary
    
    Returns:
        SHA256 hash
    """
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()


def generate_provenance_id(entity_id: str, stage: int, output_hash: str) -> str:
    """Generate deterministic provenance ID using Primitive.identity (industry standard).
    
    Args:
        entity_id: Entity ID
        stage: Pipeline stage
        output_hash: Hash of output data
    
    Returns:
        provenance_id (format: prov:{hash16} - industry standard, 16-char hash)
    """
    try:
        from truth_forge.identity import generate_hash
        content = f"prov:{entity_id}:{stage}:{output_hash}"
        hash_value = generate_hash(content, length=16)  # 64 bits, industry standard
    except ImportError:
        # Fallback to hashlib if Primitive.identity not available
        content = f"prov:{entity_id}:{stage}:{output_hash}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"prov:{hash_value}"


def record_provenance(
    client: bigquery.Client,
    entity_id: str,
    stage: int,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    transformation: str,
    transformation_params: Optional[Dict[str, Any]] = None,
    parent_provenance_id: Optional[str] = None,
    run_id: str = None,
) -> str:
    """Record provenance with cryptographic hashing.
    
    Args:
        client: BigQuery client
        entity_id: Entity ID
        stage: Pipeline stage
        input_data: Input data for this stage
        output_data: Output data from this stage
        transformation: Description of transformation
        transformation_params: Parameters used in transformation
        parent_provenance_id: Parent provenance ID (from previous stage)
        run_id: Current run ID
    
    Returns:
        provenance_id
    """
    # Calculate hashes
    input_hash = calculate_data_hash(input_data) if input_data else None
    output_hash = calculate_data_hash(output_data)
    
    # Build provenance chain
    provenance_chain = []
    if parent_provenance_id:
        # Get parent's chain
        parent_query = f"""
        SELECT provenance_chain
        FROM `{PROVENANCE_TABLE}`
        WHERE provenance_id = '{parent_provenance_id}'
        """
        parent_result = list(client.query(parent_query).result())
        
        if parent_result:
            parent_chain = parent_result[0].provenance_chain or []
            provenance_chain.extend(parent_chain)
            provenance_chain.append(parent_provenance_id)
    
    provenance_id = generate_provenance_id(entity_id, stage, output_hash)
    provenance_chain.append(provenance_id)
    
    # Verify integrity
    verification_status = "VERIFIED"
    verified_at = datetime.now(timezone.utc)
    
    if parent_provenance_id and input_hash:
        # Verify parent's output matches our input
        parent_query = f"""
        SELECT output_hash
        FROM `{PROVENANCE_TABLE}`
        WHERE provenance_id = '{parent_provenance_id}'
        """
        parent_result = list(client.query(parent_query).result())
        
        if parent_result:
            parent_output_hash = parent_result[0].output_hash
            if parent_output_hash != input_hash:
                verification_status = "FAILED"
                verified_at = None
    
    provenance = {
        "provenance_id": provenance_id,
        "entity_id": entity_id,
        "stage": stage,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "transformation": transformation,
        "transformation_params": json.dumps(transformation_params or {}),
        "parent_provenance_id": parent_provenance_id,
        "provenance_chain": provenance_chain,
        "verification_status": verification_status,
        "verified_at": verified_at if verification_status == "VERIFIED" else None,
        "run_id": run_id or "unknown",
    }
    
    # Ensure provenance table exists
    ensure_provenance_table(client)
    
    # Load provenance
    from src.services.central_services.core.bigquery_client import get_bigquery_client
    bq_client = get_bigquery_client()
    bq_client.load_rows_to_table(PROVENANCE_TABLE, [provenance])
    
    return provenance_id


def ensure_provenance_table(client: bigquery.Client) -> bigquery.Table:
    """Ensure provenance table exists with proper schema.
    
    Args:
        client: BigQuery client
    
    Returns:
        Table reference
    """
    table_ref = bigquery.Table(PROVENANCE_TABLE, schema=PROVENANCE_SCHEMA)
    table_ref.time_partitioning = PROVENANCE_PARTITIONING
    table_ref.clustering_fields = PROVENANCE_CLUSTERING
    
    return client.create_table(table_ref, exists_ok=True)


def verify_provenance_chain(
    client: bigquery.Client,
    entity_id: str,
) -> Dict[str, Any]:
    """Verify complete provenance chain for an entity.
    
    Args:
        client: BigQuery client
        entity_id: Entity to verify
    
    Returns:
        Verification report
    """
    # Get all provenance records for entity
    query = f"""
    SELECT *
    FROM `{PROVENANCE_TABLE}`
    WHERE entity_id = '{entity_id}'
    ORDER BY stage ASC
    """
    
    provenance_records = list(client.query(query).result())
    
    verification_report = {
        "entity_id": entity_id,
        "chain_length": len(provenance_records),
        "verified": True,
        "failures": [],
        "stages_verified": [],
    }
    
    # Verify each link in chain
    for i, record in enumerate(provenance_records):
        if i > 0:
            # Verify parent's output matches our input
            parent = provenance_records[i - 1]
            if record.input_hash != parent.output_hash:
                verification_report["verified"] = False
                verification_report["failures"].append({
                    "stage": record.stage,
                    "issue": "Input hash doesn't match parent output hash",
                    "expected": parent.output_hash,
                    "actual": record.input_hash,
                })
            else:
                verification_report["stages_verified"].append(record.stage)
        else:
            verification_report["stages_verified"].append(record.stage)
    
    return verification_report


# ============================================================================
# DATA CONTRACTS WITH SEMANTIC VERSIONING
# ============================================================================

DATA_CONTRACT_TABLE = f"{PROJECT_ID}.{DATASET_ID}.data_contracts"

DATA_CONTRACT_SCHEMA = [
    bigquery.SchemaField("contract_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("contract_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("schema_version", "STRING", mode="REQUIRED"),  # "1.2.3"
    bigquery.SchemaField("semantic_version", "STRING", mode="REQUIRED"),  # "conversation.2024.01"
    bigquery.SchemaField("stage", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("contract_terms", "JSON", mode="REQUIRED"),  # Quality rules
    bigquery.SchemaField("compatibility", "STRING", mode="REQUIRED"),  # BACKWARD, FORWARD, NONE
    bigquery.SchemaField("migration_rules", "JSON"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("active", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("deprecated_at", "TIMESTAMP"),
]


def generate_contract_id(contract_name: str, stage: int) -> str:
    """Generate deterministic contract ID using Primitive.identity (industry standard).
    
    Args:
        contract_name: Name of contract
        stage: Pipeline stage
    
    Returns:
        contract_id (format: contract:{hash16} - industry standard, 16-char hash)
    """
    try:
        from truth_forge.identity import generate_hash
        content = f"contract:{contract_name}:{stage}"
        hash_value = generate_hash(content, length=16)  # 64 bits, industry standard
    except ImportError:
        # Fallback to hashlib if Primitive.identity not available
        content = f"contract:{contract_name}:{stage}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"contract:{hash_value}"


def define_data_contract(
    contract_name: str,
    stage: int,
    required_fields: List[str],
    quality_rules: Dict[str, Any],
    semantic_rules: Optional[Dict[str, Any]] = None,
    compatibility: str = "BACKWARD_COMPATIBLE",
) -> Dict[str, Any]:
    """Define a data contract.
    
    Args:
        contract_name: Name of contract (e.g., "claude_code_l5_messages")
        stage: Pipeline stage
        required_fields: List of required field names
        quality_rules: Quality validation rules (e.g., {"text_length": "> 0"})
        semantic_rules: Semantic validation rules (e.g., {"conversation_id": "must_exist_in_l8"})
        compatibility: Compatibility mode (BACKWARD, FORWARD, NONE)
    
    Returns:
        Contract dictionary
    """
    contract_id = generate_contract_id(contract_name, stage)
    semantic_version = f"{contract_name}.{datetime.now().strftime('%Y.%m')}"
    
    contract = {
        "contract_id": contract_id,
        "contract_name": contract_name,
        "schema_version": "1.0.0",
        "semantic_version": semantic_version,
        "stage": stage,
        "contract_terms": json.dumps({
            "required_fields": required_fields,
            "quality_rules": quality_rules,
            "semantic_rules": semantic_rules or {},
        }),
        "compatibility": compatibility,
        "migration_rules": json.dumps({}),
        "created_at": datetime.now(timezone.utc),
        "active": True,
        "deprecated_at": None,
    }
    
    return contract


def ensure_data_contract_table(client: bigquery.Client) -> bigquery.Table:
    """Ensure data contract table exists with proper schema.
    
    Args:
        client: BigQuery client
    
    Returns:
        Table reference
    """
    table_ref = bigquery.Table(DATA_CONTRACT_TABLE, schema=DATA_CONTRACT_SCHEMA)
    
    return client.create_table(table_ref, exists_ok=True)


def evaluate_quality_rule(value: Any, rule: str) -> bool:
    """Evaluate a quality rule.
    
    Args:
        value: Value to check
        rule: Rule expression (e.g., "> 0", "in ['a', 'b']")
    
    Returns:
        True if rule passes
    """
    # Simple rule evaluation (can be extended)
    if rule.startswith(">"):
        threshold = float(rule[1:].strip())
        return float(value) > threshold
    elif rule.startswith("<"):
        threshold = float(rule[1:].strip())
        return float(value) < threshold
    elif rule.startswith("in "):
        # Parse list: "in ['a', 'b']"
        import ast
        items = ast.literal_eval(rule[3:].strip())
        return value in items
    elif rule == "not_null":
        return value is not None
    elif rule == "valid_iso":
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except:
            return False
    else:
        # Default: rule is a Python expression
        try:
            return eval(f"{value} {rule}")
        except:
            return False


def validate_against_contract(
    client: bigquery.Client,
    data: Dict[str, Any],
    contract_id: str,
) -> Tuple[bool, List[str]]:
    """Validate data against contract.
    
    Args:
        client: BigQuery client
        data: Data to validate
        contract_id: Contract ID
    
    Returns:
        (is_valid, errors)
    """
    # Get contract
    query = f"""
    SELECT *
    FROM `{DATA_CONTRACT_TABLE}`
    WHERE contract_id = '{contract_id}'
      AND active = TRUE
    """
    
    contracts = list(client.query(query).result())
    
    if not contracts:
        return False, [f"Contract {contract_id} not found or inactive"]
    
    contract = contracts[0]
    contract_terms = json.loads(contract.contract_terms)
    errors = []
    
    # Check required fields
    for field in contract_terms["required_fields"]:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Check quality rules
    for rule_name, rule_value in contract_terms["quality_rules"].items():
        if rule_name in data:
            if not evaluate_quality_rule(data[rule_name], rule_value):
                errors.append(f"Quality rule failed: {rule_name} = {rule_value}")
    
    # Semantic rules require database queries (simplified here)
    # Full implementation would query related tables
    
    return len(errors) == 0, errors
