# Logging and Observability System - Comprehensive Guide

**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-01-21

---

## Overview

The Truth Engine logging and observability system provides enterprise-grade logging with:

- **Structured JSON logging** (OpenTelemetry-aligned)
- **Tiered retention policies** (hot/warm/cold/archive)
- **Federation-aware aggregation** (cross-organism, Genesis/Seed)
- **Cloud storage integration** (automated sync)
- **Log insights and analytics** (pattern recognition)
- **Automated lifecycle management** (compression, tier transitions)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Logging Service                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Hot Tier   │→ │  Warm Tier   │→ │  Cold Tier   │      │
│  │  (0-30 days) │  │ (30-90 days) │  │ (90-365 days)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            ↓                                 │
│                    ┌──────────────┐                         │
│                    │ Archive Tier │                         │
│                    │  (1+ years)  │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Federation Aggregator                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Organism A  │  │  Organism B  │  │  Organism C  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            ↓                                 │
│              Cross-Organism Correlation                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Cloud Storage Sync                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  GCP Storage │  │  AWS S3      │  │  Azure Blob  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Log Retention Policies

### By Category

| Category | Hot (Days) | Warm (Days) | Cold (Days) | Archive (Days) | Total Retention |
|----------|------------|-------------|-------------|----------------|-----------------|
| **Audit** | 90 | 365 | 1095 (3y) | 1825 (5y) | **5+ years** |
| **Security** | 90 | 365 | 1095 (3y) | 1825 (5y) | **5+ years** |
| **Federation** | 365 | 730 | 1095 (3y) | 1825 (5y) | **5+ years** |
| **Operation** | 30 | 90 | 365 (1y) | 730 (2y) | **2 years** |
| **Application** | 30 | 90 | 365 (1y) | 730 (2y) | **2 years** |
| **Performance** | 14 | 90 | 365 (1y) | 730 (2y) | **2 years** |
| **Debug** | 7 | - | - | - | **7 days** |
| **Insight** | 365 | 730 | 1095 (3y) | 1095 (3y) | **3 years** |

### Storage Tiers

- **Hot**: Fast access, uncompressed, recent logs (0-30 days typically)
- **Warm**: Moderate access, may be compressed, recent logs (30-90 days)
- **Cold**: Infrequent access, compressed, older logs (90 days - 1 year)
- **Archive**: Rare access, highly compressed, long-term retention (1+ years)

---

## Local Storage

### Default Location

```
{workspace_root}/.truth_engine/observability/logs/
├── hot/          # Recent logs (0-30 days)
│   ├── 2026-01-21.jsonl
│   └── 2026-01-20.jsonl
├── warm/         # Moderate age (30-90 days)
│   ├── 2025-12-15.jsonl.gz
│   └── 2025-12-14.jsonl.gz
├── cold/         # Older logs (90-365 days)
│   ├── 2025-06-01.jsonl.gz
│   └── 2025-05-31.jsonl.gz
└── archive/      # Long-term (1+ years)
    ├── 2024-01-01.jsonl.gz
    └── 2023-12-31.jsonl.gz
```

### File Naming

- Format: `YYYY-MM-DD.jsonl` (uncompressed) or `YYYY-MM-DD.jsonl.gz` (compressed)
- One file per day per tier
- Automatic compression when moving to warm/cold/archive tiers

---

## Cloud Storage

### When Logs Are Synced

Logs are synced to cloud storage:

1. **Immediately**: Security and audit logs
2. **Daily**: All logs from previous day (batch sync)
3. **On-demand**: Manual sync via API

### Cloud Storage Locations

#### Google Cloud Platform (GCP)

```
gs://truth-engine-logs/{organism_id}/{genesis_id}/{seed_id}/
├── hot/
│   └── {date}.jsonl
├── warm/
│   └── {date}.jsonl.gz
├── cold/
│   └── {date}.jsonl.gz
└── archive/
    └── {date}.jsonl.gz
```

#### AWS S3

```
s3://truth-engine-logs/{organism_id}/{genesis_id}/{seed_id}/
├── hot/
├── warm/
├── cold/
└── archive/
```

#### Azure Blob Storage

```
https://{account}.blob.core.windows.net/truth-engine-logs/{organism_id}/{genesis_id}/{seed_id}/
├── hot/
├── warm/
├── cold/
└── archive/
```

### Cloud Storage Retention

- **Hot/Warm**: Same as local retention
- **Cold/Archive**: Extended retention (up to 10 years for audit/security)
- **Cost optimization**: Automatic transition to cheaper storage tiers

---

## Federation Integration

### Cross-Organism Log Correlation

The federation aggregator enables:

- **Trace correlation**: Follow a request across multiple organisms
- **Cross-organism queries**: Query logs from all organisms simultaneously
- **Genesis/Seed boundaries**: Correlate logs across Genesis and Seed divides
- **Pattern recognition**: Identify patterns across the federation

### Example: Federation Query

```python
from Primitive.observability.federation_aggregator import (
    FederationAggregator,
    FederationQuery,
)

# Query logs across all organisms for a trace
query = FederationQuery(
    trace_id="trace_abc123",
    since=datetime.now(timezone.utc) - timedelta(hours=1),
)

result = aggregator.query_federation(query)
print(f"Found {len(result.entries)} logs across {result.organism_count} organisms")
```

---

## Usage Examples

### Basic Logging

```python
from Primitive.observability.logging_service import (
    LoggingService,
    LogLevel,
    LogCategory,
)

# Get logging service
service = LoggingService(
    organism_id="organism_123",
    genesis_id="genesis_456",
    seed_id="seed_789",
)

# Log an event
service.log(
    level=LogLevel.INFO,
    message="Operation completed successfully",
    component="data_processor",
    service_name="processing_service",
    service_version="1.0.0",
    attributes={
        "operation": "transform_data",
        "duration_ms": 150,
        "records_processed": 1000,
    },
    category=LogCategory.APPLICATION,
)
```

### Querying Logs

```python
# Query recent errors
errors = service.query(
    level=LogLevel.ERROR,
    since=datetime.now(timezone.utc) - timedelta(days=1),
    limit=100,
)

# Query by trace ID
trace_logs = service.query(
    trace_id="trace_abc123",
    limit=1000,
)

# Query by component
component_logs = service.query(
    component="data_processor",
    since=datetime.now(timezone.utc) - timedelta(hours=6),
)
```

### Lifecycle Management

```python
from Primitive.observability.lifecycle_manager import LifecycleManager

# Run lifecycle management (move, compress, delete)
manager = LifecycleManager(service)
stats = manager.run_lifecycle()

print(f"Processed {stats.files_processed} files")
print(f"Moved {stats.files_moved} files to next tier")
print(f"Compressed {stats.files_compressed} files")
print(f"Deleted {stats.files_deleted} expired files")
print(f"Freed {stats.bytes_freed} bytes")

# Get storage statistics
storage_stats = manager.get_storage_stats()
for tier, stats in storage_stats.items():
    print(f"{tier}: {stats['files']} files, {stats['size_mb']} MB")
```

---

## Log Insights

### Automatic Insights

The system automatically generates insights:

- **Error patterns**: Recurring errors across services
- **Performance trends**: Latency patterns over time
- **Federation patterns**: Cross-organism behavior
- **Anomaly detection**: Unusual log patterns

### Accessing Insights

```python
from Primitive.observability.insights_service import InsightsService

insights = InsightsService(service)

# Get error insights
error_insights = insights.get_error_insights(days=7)

# Get performance insights
perf_insights = insights.get_performance_insights(days=30)

# Get federation insights
federation_insights = insights.get_federation_insights(days=90)
```

---

## Best Practices

### 1. Use Structured Logging

✅ **Good**:
```python
service.log(
    level=LogLevel.INFO,
    message="User authenticated",
    attributes={
        "user_id": "user_123",
        "method": "oauth",
        "duration_ms": 45,
    },
)
```

❌ **Bad**:
```python
logger.info(f"User user_123 authenticated via oauth in 45ms")
```

### 2. Include Correlation IDs

Always include correlation IDs for distributed tracing:

```python
# Correlation IDs are automatically included via context
service.log(
    level=LogLevel.INFO,
    message="Processing request",
    # trace_id, correlation_id, run_id automatically added
)
```

### 3. Choose Appropriate Categories

- **AUDIT**: Security events, access logs
- **SECURITY**: Security violations, threats
- **FEDERATION**: Cross-organism events
- **OPERATION**: System operations, deployments
- **APPLICATION**: Application-level events
- **PERFORMANCE**: Performance metrics, latency
- **DEBUG**: Debug information (short retention)

### 4. Set Appropriate Log Levels

- **TRACE**: Very detailed, development only
- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages
- **WARN**: Warning messages
- **ERROR**: Error events
- **FATAL**: Critical errors

---

## Monitoring and Alerts

### Storage Monitoring

Monitor storage usage:

```python
storage_stats = manager.get_storage_stats()
total_size = sum(s['size_bytes'] for s in storage_stats.values())

if total_size > 10 * 1024 * 1024 * 1024:  # 10 GB
    alert("Log storage exceeds 10 GB")
```

### Lifecycle Monitoring

Run lifecycle management regularly:

```python
# Run daily via cron or scheduler
stats = manager.run_lifecycle()

if stats.errors:
    alert(f"Lifecycle management errors: {stats.errors}")
```

---

## Cost Optimization

### Strategies

1. **Compression**: Automatic compression for warm/cold/archive tiers
2. **Retention**: Appropriate retention based on category
3. **Sampling**: Sample debug logs (not implemented yet)
4. **Tier transitions**: Move to cheaper storage automatically
5. **Cloud tiering**: Use cloud storage lifecycle policies

### Estimated Costs

- **Hot storage**: ~$0.023/GB/month (local SSD)
- **Warm storage**: ~$0.010/GB/month (local HDD)
- **Cold storage**: ~$0.004/GB/month (compressed)
- **Archive storage**: ~$0.001/GB/month (highly compressed)
- **Cloud storage**: Varies by provider and tier

---

## Troubleshooting

### Logs Not Appearing

1. Check storage path exists and is writable
2. Verify logging service is initialized
3. Check log level (DEBUG logs may be filtered)

### Storage Growing Too Fast

1. Run lifecycle management more frequently
2. Review retention policies
3. Check for excessive debug logging
4. Consider log sampling

### Federation Queries Slow

1. Limit query time range
2. Use specific organism filters
3. Query specific tiers (hot/warm only)
4. Consider pre-aggregation

---

## Implementation Status

### ✅ Completed

- ✅ Structured logging with retention policies
- ✅ Automated lifecycle management
- ✅ Federation-aware aggregation
- ✅ Cloud storage integration (GCP/AWS/Azure)
- ✅ Automated sync scheduling
- ✅ Real-time log streaming (WebSocket/SSE)
- ✅ Log-based alerting
- ✅ Insights and analytics
- ✅ Anomaly detection
- ✅ Performance trend analysis
- ✅ Integration tests

### Future Enhancements (Optional)

- [ ] Log sampling for high-volume debug logs
- [ ] ML-based advanced analytics
- [ ] Integration with external observability tools (Grafana, Datadog)
- [ ] Log replay capabilities
- [ ] Advanced compression algorithms
- [ ] Log-based metrics generation

---

## References

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Structured Logging Best Practices](https://uptrace.dev/blog/structured-logging.html)
- [Log Retention Policies](https://aws-observability.github.io/observability-best-practices/tools/logs/)
- [Federation Patterns](https://moss.sh/reviews/multi-cloud-monitoring-strategies/)
