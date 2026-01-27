# Logging & Observability - Quick Reference

## Your Questions Answered

### 1. How Long Do Logs Persist Locally?

**Answer**: Depends on log category:

| Category | Local Retention |
|----------|----------------|
| **Audit/Security** | 5+ years (with tier transitions) |
| **Federation** | 5+ years |
| **Operation/Application** | 2 years |
| **Performance** | 2 years |
| **Debug** | 7 days only |
| **Insights** | 3 years |

**Storage Tiers**:
- **Hot** (0-30 days): Fast, uncompressed
- **Warm** (30-90 days): Compressed
- **Cold** (90-365 days): Highly compressed
- **Archive** (1+ years): Maximum compression

**Location**: `{workspace}/.truth_engine/observability/logs/`

---

### 2. When and Where Are Logs Stored to Cloud?

**When**:
- **Immediately**: Security and audit logs
- **Daily**: All logs from previous day (batch sync at 2 AM UTC)
- **On-demand**: Manual sync via API

**Where**:

#### Google Cloud Platform
```
gs://truth-engine-logs/{organism_id}/{genesis_id}/{seed_id}/
```

#### AWS S3
```
s3://truth-engine-logs/{organism_id}/{genesis_id}/{seed_id}/
```

#### Azure Blob Storage
```
https://{account}.blob.core.windows.net/truth-engine-logs/{organism_id}/{genesis_id}/{seed_id}/
```

**Cloud Retention**: Extended retention (up to 10 years for audit/security)

---

### 3. How to Leverage Logs for Insights?

#### Basic Querying

```python
from Primitive.observability.logging_service import LoggingService, LogLevel

service = LoggingService()

# Find all errors in last 24 hours
errors = service.query(
    level=LogLevel.ERROR,
    since=datetime.now(timezone.utc) - timedelta(days=1),
)

# Find logs for a specific trace
trace_logs = service.query(trace_id="trace_abc123")

# Find logs by component
component_logs = service.query(component="data_processor")
```

#### Federation Queries

```python
from Primitive.observability.federation_aggregator import (
    FederationAggregator,
    FederationQuery,
)

# Query across all organisms
query = FederationQuery(
    trace_id="trace_abc123",
    organism_ids=["org1", "org2"],  # Optional: specific organisms
    since=datetime.now(timezone.utc) - timedelta(hours=1),
)

result = aggregator.query_federation(query)
print(f"Found {len(result.entries)} logs across {result.organism_count} organisms")
```

#### Storage Statistics

```python
from Primitive.observability.lifecycle_manager import LifecycleManager

manager = LifecycleManager(service)
stats = manager.get_storage_stats()

for tier, tier_stats in stats.items():
    print(f"{tier}: {tier_stats['files']} files, {tier_stats['size_mb']} MB")
```

#### Service Statistics

```python
stats = service.get_stats()
print(f"Total logs: {stats['total_logs']}")
print(f"By level: {stats['by_level']}")
print(f"By category: {stats['by_category']}")
```

---

## Common Tasks

### Log an Event

```python
service.log(
    level=LogLevel.INFO,
    message="Operation completed",
    component="my_service",
    attributes={"duration_ms": 150, "records": 1000},
)
```

### Run Lifecycle Management

```python
# Moves logs between tiers, compresses, deletes expired
stats = manager.run_lifecycle()
```

### Query Federation Logs

```python
# Get all logs for a trace across organisms
logs = aggregator.correlate_trace("trace_abc123")
```

---

## File Locations

### Local Storage
```
.truth_engine/observability/logs/
├── hot/          # Recent (0-30 days)
├── warm/         # Moderate (30-90 days)
├── cold/         # Older (90-365 days)
└── archive/      # Long-term (1+ years)
```

### Cloud Storage
- **GCP**: `gs://truth-engine-logs/{organism}/{genesis}/{seed}/`
- **AWS**: `s3://truth-engine-logs/{organism}/{genesis}/{seed}/`
- **Azure**: `https://{account}.blob.core.windows.net/truth-engine-logs/...`

---

## Retention Summary

| Category | Hot | Warm | Cold | Archive | Total |
|----------|-----|------|------|---------|-------|
| Audit | 90d | 365d | 3y | 5y | **5+ years** |
| Security | 90d | 365d | 3y | 5y | **5+ years** |
| Federation | 365d | 730d | 3y | 5y | **5+ years** |
| Operation | 30d | 90d | 1y | 2y | **2 years** |
| Application | 30d | 90d | 1y | 2y | **2 years** |
| Performance | 14d | 90d | 1y | 2y | **2 years** |
| Debug | 7d | - | - | - | **7 days** |
| Insight | 365d | 730d | 3y | 3y | **3 years** |

---

## Quick Commands

```python
# Initialize service
service = LoggingService(
    organism_id="my_org",
    genesis_id="genesis_123",
    seed_id="seed_456",
)

# Log
service.log(LogLevel.INFO, "Message", component="service")

# Query
logs = service.query(level=LogLevel.ERROR, since=datetime.now() - timedelta(days=1))

# Lifecycle
manager = LifecycleManager(service)
stats = manager.run_lifecycle()

# Federation
aggregator = FederationAggregator({"org1": service1, "org2": service2})
result = aggregator.query_federation(FederationQuery(trace_id="trace_123"))
```

---

For detailed documentation, see [LOGGING_OBSERVABILITY_SYSTEM.md](./LOGGING_OBSERVABILITY_SYSTEM.md)
