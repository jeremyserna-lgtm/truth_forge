# Observability System - Integration Guide

**How to integrate the observability system into your workflows**

---

## Quick Integration

### Step 1: Initialize Orchestrator

```python
from Primitive.observability import (
    ObservabilityOrchestrator,
    OrchestratorConfig,
    CloudConfig,
    CloudProvider,
    LogLevel,
)

# Configure
config = OrchestratorConfig(
    organism_id="your_organism_id",
    genesis_id="your_genesis_id",
    seed_id="your_seed_id",
    
    # Optional: Cloud storage
    cloud_providers=[
        CloudConfig(
            provider=CloudProvider.GCP,  # or AWS, AZURE
            bucket_name="your-bucket-name",
            prefix="your_organism/your_genesis/your_seed",
            gcp_project="your-project",  # GCP only
        ),
    ],
    
    # Enable features
    lifecycle_enabled=True,
    sync_enabled=True,  # Requires cloud_providers
    streaming_enabled=True,
    alerting_enabled=True,
    insights_enabled=True,
)

# Start
orchestrator = ObservabilityOrchestrator(config)
orchestrator.start()
```

### Step 2: Use in Your Code

```python
# Log events
orchestrator.log(
    LogLevel.INFO,
    "Operation completed",
    component="your_service",
    attributes={"duration_ms": 150, "records": 1000},
)

# Query logs
service = orchestrator.logging_service
logs = service.query(
    level=LogLevel.ERROR,
    since=datetime.now(timezone.utc) - timedelta(days=1),
)

# Get insights
insights = orchestrator.get_insights(days=7)
```

### Step 3: Monitor Health

```python
health = orchestrator.get_health()
print(f"Status: {health['status']}")
print(f"Active alerts: {health['active_alerts']}")
print(f"Storage: {health['storage']}")
```

---

## Integration with Existing Code

### Replace Basic Logging

**Before**:
```python
from Primitive.core import get_logger
logger = get_logger(__name__)
logger.info("Operation completed")
```

**After**:
```python
from Primitive.observability import get_orchestrator, LogLevel

orchestrator = get_orchestrator(config)
orchestrator.log(
    LogLevel.INFO,
    "Operation completed",
    component=__name__,
    attributes={"operation": "process_data"},
)
```

### Integration with Tracing

The observability system integrates with existing OpenTelemetry tracing:

```python
from Primitive.observability.tracing import traced
from Primitive.observability import get_orchestrator, LogLevel

orchestrator = get_orchestrator(config)

@traced("process_data")
def process_data(data):
    # Automatic tracing + logging
    orchestrator.log(
        LogLevel.INFO,
        "Processing data",
        component="data_processor",
        attributes={"data_size": len(data)},
    )
    # Trace ID automatically included in log
```

---

## Federation Integration

### Multi-Organism Setup

```python
# Organism 1
service1 = LoggingService(organism_id="org_1", genesis_id="genesis_123")
service1.log(LogLevel.INFO, "Event in org 1")

# Organism 2
service2 = LoggingService(organism_id="org_2", genesis_id="genesis_123")
service2.log(LogLevel.INFO, "Event in org 2")

# Aggregate
from Primitive.observability import FederationAggregator, FederationQuery

aggregator = FederationAggregator({
    "org_1": service1,
    "org_2": service2,
})

# Query across federation
result = aggregator.query_federation(
    FederationQuery(genesis_id="genesis_123")
)
```

---

## Cloud Storage Setup

### GCP Setup

```python
from Primitive.observability import CloudStorage, CloudConfig, CloudProvider

cloud = CloudStorage(logging_service)

# Add GCP provider
cloud.add_provider(CloudConfig(
    provider=CloudProvider.GCP,
    bucket_name="truth-engine-logs",
    prefix="organism_123/genesis_456/seed_789",
    gcp_project="my-project",
    credentials_path="/path/to/service-account.json",  # Optional
    compression=True,
    encryption=True,
))

# Sync
results = cloud.sync(mode=SyncMode.DAILY)
```

### AWS Setup

```python
cloud.add_provider(CloudConfig(
    provider=CloudProvider.AWS,
    bucket_name="truth-engine-logs",
    prefix="organism_123/genesis_456/seed_789",
    region="us-east-1",
    aws_profile="default",  # Optional
    compression=True,
    encryption=True,
))
```

### Azure Setup

```python
cloud.add_provider(CloudConfig(
    provider=CloudProvider.AZURE,
    bucket_name="truth-engine-logs",
    prefix="organism_123/genesis_456/seed_789",
    azure_account_name="myaccount",
    azure_account_key="key",  # Or use Azure Identity
    compression=True,
    encryption=True,
))
```

---

## Alerting Setup

### Define Alert Rules

```python
from Primitive.observability import (
    AlertingService,
    AlertRule,
    AlertCondition,
    AlertSeverity,
)

alerting = AlertingService(logging_service, insights_service)

# High error rate alert
alerting.add_rule(AlertRule(
    rule_id="high_error_rate",
    name="High Error Rate",
    condition=AlertCondition.ERROR_RATE,
    severity=AlertSeverity.CRITICAL,
    threshold=0.1,  # 10%
    time_window_minutes=15,
    channels=["log", "email"],  # or "webhook"
    description="Alert when error rate exceeds 10% in 15 minutes",
))

# Error count alert
alerting.add_rule(AlertRule(
    rule_id="error_count",
    name="High Error Count",
    condition=AlertCondition.ERROR_COUNT,
    severity=AlertSeverity.WARNING,
    threshold=10,
    time_window_minutes=60,
    component="database",  # Optional: specific component
))

# Anomaly alert
alerting.add_rule(AlertRule(
    rule_id="anomaly_detected",
    name="Anomaly Detected",
    condition=AlertCondition.ANOMALY_DETECTED,
    severity=AlertSeverity.CRITICAL,
    time_window_minutes=30,
))
```

### Evaluate Alerts

```python
# Automatic (via orchestrator)
# Alerts are evaluated automatically every 5 minutes

# Manual
alerts = alerting.evaluate()

# Get active alerts
active = alerting.get_active_alerts(severity=AlertSeverity.CRITICAL)
```

---

## Insights Usage

### Error Analysis

```python
insights = InsightsService(logging_service)

# Get error insights
error_insights = insights.get_error_insights(days=7)
print(f"Total errors: {error_insights['total_errors']}")
print(f"Top patterns:")
for pattern in error_insights['top_patterns'][:5]:
    print(f"  - {pattern['message_template']}: {pattern['count']} times")
```

### Performance Analysis

```python
# Get performance trends
perf_insights = insights.get_performance_insights(days=30)

for trend in perf_insights:
    print(f"{trend.component}:")
    print(f"  Mean: {trend.mean:.2f}ms")
    print(f"  P95: {trend.p95:.2f}ms")
    print(f"  P99: {trend.p99:.2f}ms")
    print(f"  Trend: {trend.trend}")
```

### Anomaly Detection

```python
# Detect anomalies
anomalies = insights.detect_anomalies(days=1)

for anomaly in anomalies:
    print(f"Anomaly: {anomaly.description}")
    print(f"  Component: {anomaly.component}")
    print(f"  Severity: {anomaly.severity}")
    print(f"  Type: {anomaly.anomaly_type}")
```

---

## Real-time Streaming

### WebSocket Integration

```python
# Get WebSocket handler
streaming = StreamingService(logging_service)
streaming.start_monitoring()

handler = streaming.get_websocket_handler()

# Use with WebSocket server (e.g., FastAPI, aiohttp)
# @app.websocket("/logs")
# async def websocket_endpoint(websocket):
#     await handler(websocket)
```

### SSE Integration

```python
# Get SSE generator
sse_generator = streaming.get_sse_handler(
    filter=StreamFilter(level=LogLevel.ERROR)
)

# Use with FastAPI
# @app.get("/logs/stream")
# async def stream_logs():
#     return StreamingResponse(sse_generator(), media_type="text/event-stream")
```

---

## Maintenance Tasks

### Run Lifecycle Management

```python
# Manual
manager = orchestrator.lifecycle_manager
stats = manager.run_lifecycle()

# Automatic (via orchestrator)
# Runs every 24 hours by default
```

### Manual Cloud Sync

```python
# Manual sync
cloud = orchestrator.cloud_storage
results = cloud.sync(mode=SyncMode.ON_DEMAND)

# Check sync status
for provider, result in results.items():
    print(f"{provider}: {result.files_synced} files, {result.errors}")
```

### Monitor Storage

```python
manager = orchestrator.lifecycle_manager
storage_stats = manager.get_storage_stats()

for tier, stats in storage_stats.items():
    print(f"{tier}: {stats['files']} files, {stats['size_mb']} MB")
```

---

## Best Practices

1. **Use structured logging**: Always include attributes, not just messages
2. **Set appropriate categories**: Use categories to control retention
3. **Include correlation IDs**: Automatically included via context
4. **Monitor storage**: Check storage stats regularly
5. **Run lifecycle**: Ensure lifecycle management runs regularly
6. **Configure alerts**: Set up alerts for critical conditions
7. **Review insights**: Regularly review insights for patterns

---

## Troubleshooting

### Logs Not Appearing

1. Check storage path exists and is writable
2. Verify orchestrator is started
3. Check log level (DEBUG logs may be filtered)

### Storage Growing Too Fast

1. Run lifecycle management
2. Review retention policies
3. Check for excessive debug logging
4. Adjust retention policies if needed

### Cloud Sync Failing

1. Verify cloud credentials
2. Check network connectivity
3. Verify bucket/container exists
4. Check sync logs for errors

### Federation Queries Slow

1. Limit query time range
2. Use specific organism filters
3. Query specific tiers only (hot/warm)
4. Consider pre-aggregation

---

For complete API documentation, see [COMPLETE_IMPLEMENTATION.md](./COMPLETE_IMPLEMENTATION.md)
