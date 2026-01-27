# GCP Exports Insights Analysis

**Generated**: 2025-12-22
**Project**: flash-clover-464719-g1
**Author**: Claude Code + GCP Operations Service

---

## Executive Summary

This document synthesizes insights from all GCP BigQuery exports to provide a unified view of Truth Engine's operational health, cost patterns, and security posture.

### Key Findings

| Category | Status | Key Metric |
|----------|--------|------------|
| **Cost Health** | WARNING | $993.63 spike on Dec 17 (BigQuery 98.7% of spend) |
| **Security Posture** | CRITICAL | 4 IAM overprivilege alerts (3 GCP-managed, expected) |
| **Data Volume** | HEALTHY | 238.5 GB across spine dataset, 51.7M+ entities |
| **Operations** | HEALTHY | 59 tracked pipeline runs this week |

---

## 1. Cost Intelligence

### 1.1 Service Cost Breakdown (Last 7 Days)

| Service | Cost | % of Total | Trend |
|---------|------|------------|-------|
| BigQuery | $995.32 | 98.7% | Spike on Dec 17 |
| Artifact Registry | $6.55 | 0.6% | Stable |
| Gemini API | $2.43 | 0.2% | Minimal |
| Compute Engine | $1.89 | 0.2% | Stable |
| Secret Manager | $1.09 | 0.1% | Stable |
| Cloud Storage | $0.74 | 0.07% | Stable |
| Other | $0.41 | 0.04% | Stable |
| **Total** | **$1,008.49** | 100% | - |

### 1.2 Daily Cost Trend

```
Date        Cost      Visual
─────────────────────────────────────────
Dec 08    $42.77     ████▌
Dec 09     $7.96     █
Dec 10     $1.41     ▏
Dec 11     $1.41     ▏
Dec 12     $6.23     ▋
Dec 13     $2.30     ▎
Dec 14     $1.88     ▎
Dec 15     $4.47     ▌
Dec 16     $1.64     ▎
Dec 17   $993.63     ████████████████████████████████████████ ← INCIDENT
Dec 18     $2.27     ▎
Dec 19     $2.06     ▎
Dec 20     $1.49     ▏
Dec 21     $2.44     ▎
Dec 22     $0.49     ▏
```

**Analysis**: The Dec 17 cost spike of $993.63 was caused by uncontrolled BigQuery queries. This triggered implementation of:
- Per-query byte limits (1GB max)
- Daily spend caps ($100)
- Runtime cost protection

### 1.3 BigQuery Cost Attribution

Top cost drivers are individual query jobs (Analysis SKU):

| Resource Type | Cost | Description |
|---------------|------|-------------|
| Query Jobs | $0.14-0.18 each | Ad-hoc analysis queries |
| Total Query Cost | ~$995.32 | 98.7% of all spending |

**Root Cause**: Large table scans without partition pruning. The `spine.entity_unified` table (6.87 GB) and pipeline stage tables (up to 37 GB each) were queried without WHERE clauses on partition columns.

### 1.4 Cost-to-Value Mapping

| Truth Engine Component | Storage | Monthly Query Cost | Value Generated |
|------------------------|---------|-------------------|-----------------|
| `entity_embeddings` | 36.94 GB | ~$2.31 | Semantic search, similarity |
| `chatgpt_web_ingestion_*` | 120+ GB | ~$7.50 | 351 conversations, 51.7M entities |
| `entity_tokens` | 15.7 GB | ~$0.98 | L1 token analysis |
| Governance tables | ~1 GB | ~$0.06 | Cost tracking, audit |

---

## 2. Security Posture

### 2.1 IAM Overprivilege Analysis

| Account | Role | Total Permissions | Used | Usage % | Risk | Action |
|---------|------|-------------------|------|---------|------|--------|
| jeremy.serna@gmail.com | Owner | 12,371 | 469 | 3.8% | Expected | None |
| 81233637196-compute@ | Editor | 10,914 | 37 | 0.3% | Low | Optional right-size |
| 81233637196@cloudservices | Editor | 10,900 | 0 | 0% | GCP-Managed | DO NOT MODIFY |
| flash-clover@appspot | Editor | 10,900 | 1 | 0.01% | Low | Optional |

**Interpretation**:
- **Owner account**: Expected. You need these permissions as project owner.
- **Cloud Services SA**: GCP-managed internal account. Modifying will break GCP.
- **Compute SA**: Used by Cloud Run. Could be right-sized but low priority.
- **App Engine SA**: Minimal usage. Can be reviewed if App Engine isn't used.

### 2.2 Audit Log Activity (Last 7 Days)

| Actor | Actions | Unique Methods |
|-------|---------|----------------|
| gcp-sa-logging (GCP) | 12 | 4 |
| jeremy.serna@gmail.com | 10 | 6 |

**Finding**: All activity is expected. The logging service account creates BigQuery tables for audit log export. Your account performs normal development operations.

### 2.3 Unified Alerts

| Alert Type | Severity | Count | Status |
|------------|----------|-------|--------|
| IAM_OVERPRIVILEGED | CRITICAL | 4 | Reviewed (see 2.1) |
| Cost Anomalies | - | 0 | Resolved |

---

## 3. Infrastructure Integration

### 3.1 Data Flow: GCP Exports → Truth Engine

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GCP EXPORT SOURCES                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Billing (us-central1)              Audit Logs (US)                 │
│  └── google_cost_pricing            └── audit_logs                  │
│      ├── gcp_billing_export_v1_*        ├── cloudaudit_*_activity   │
│      └── gcp_billing_export_resource    └── cloudaudit_*_data_access│
│                                                                      │
│  Recommender (US)                   Carbon Footprint (US)           │
│  └── recommender_insights           └── carbon_footprint            │
│      └── iam_policy_insights            └── (pending export)        │
│                                                                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TRUTH ENGINE SERVICES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  GCPOperationsService              SecurityPostureMonitor           │
│  ├── get_cost_summary()            ├── get_iam_risks()              │
│  ├── get_operational_health()      ├── get_unusual_activity()       │
│  └── get_all_alerts()              └── assess_security_posture()    │
│                                                                      │
│  CostAttributionService            Pre-Run Validator                │
│  ├── estimate_query_cost()         ├── check_operational_health()   │
│  ├── get_pipeline_cost_report()    └── validate_before_run()        │
│  └── get_cost_optimization_recommendations()                        │
│                                                                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GOVERNANCE OUTPUTS                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BigQuery Views                    CLI Tools                        │
│  ├── governance.unified_alerts     └── tools/operational_health.py  │
│  ├── security.iam_security_alerts      ├── --costs                  │
│  ├── security.admin_activity_summary   ├── --security               │
│  └── governance.operations_dashboard   └── --alerts                 │
│                                                                      │
│  Enforcement                       Monitoring                       │
│  ├── Pre-commit hooks (45 rules)   ├── Cost anomaly detection       │
│  ├── Runtime protection            ├── Security posture tracking    │
│  └── Per-query byte limits         └── Audit trail analysis         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Service Connections

| Service | Data Source | Update Frequency | Integration Point |
|---------|-------------|------------------|-------------------|
| GCPOperationsService | Billing Export | Real-time | `get_cost_summary()` |
| GCPOperationsService | Audit Logs | Real-time | `get_recent_admin_activity()` |
| SecurityPostureMonitor | Recommender | On-demand | `get_iam_risks()` |
| CostAttributionService | governance.process_costs | Per-operation | `get_pipeline_cost_report()` |
| Pre-Run Validator | All services | Per-run | `validate_before_run()` |

### 3.3 Truth Engine Data Volumes

| Table | Size | Rows | Description |
|-------|------|------|-------------|
| entity_embeddings | 36.94 GB | 537,575 | Semantic vectors for search |
| chatgpt_web_ingestion_stage_12 | 36.44 GB | 103,493,552 | L2 word entities |
| chatgpt_web_ingestion_stage_14 | 29.52 GB | 51,753,646 | Final tokens |
| entity_tokens | 15.70 GB | 39,878,305 | L1 token store |
| **Total spine dataset** | **~238 GB** | **~300M rows** | Full entity hierarchy |

---

## 4. Recommendations

### 4.1 Cost Optimization

| Priority | Recommendation | Potential Savings | Effort |
|----------|----------------|-------------------|--------|
| HIGH | Add partition filters to queries | ~$900/incident | Low |
| HIGH | Use query result caching | ~10-20% | Low |
| HIGH | Deploy Billing Guardian | Prevents $1000+ incidents | Medium |
| MEDIUM | Archive stage tables after pipeline completion | $2-3/month | Medium |
| LOW | Move to BigQuery slots ($2,000/month) | Variable | High |

### 4.2 Billing Guardian (NEW)

A Cloud Function that automatically disables billing when budget thresholds are exceeded.

**Location**: `architect_central_services/cloud_run_jobs/billing_guardian/`

**Architecture**:
```
GCP Budget ($150/day)
    │
    ▼ Pub/Sub notification
Billing Guardian Function
    │
    ├── Log to BigQuery (governance.billing_guardian_log)
    ├── Send Slack notification (optional)
    └── Disable billing (if not simulating)
```

**Why event-driven (not polling)**:
- Immediate response (no 5-minute gaps)
- Uses GCP's native budget monitoring
- No additional query costs
- Google's official recommended pattern

**Deploy command**:
```bash
gcloud functions deploy billing-guardian \
  --gen2 --runtime=python311 --region=us-central1 \
  --entry-point=stop_billing \
  --trigger-topic=billing-alerts \
  --set-env-vars=SIMULATE_DEACTIVATION=true
```

See [Billing Guardian README](../architect_central_services/cloud_run_jobs/billing_guardian/README.md) for full setup instructions.

### 4.3 Security Hardening

| Priority | Recommendation | Risk Reduced | Effort |
|----------|----------------|--------------|--------|
| LOW | Right-size compute SA | Minimal | Medium |
| INFO | Document expected IAM alerts | Clarity | Low |

### 4.4 Operational Improvements

| Priority | Recommendation | Benefit | Effort |
|----------|----------------|---------|--------|
| MEDIUM | Schedule daily recommender export | Fresh security data | Low |
| MEDIUM | Enable Carbon Footprint export | ESG tracking | 5 min |
| LOW | Add cost alerts at $50/day | Early warning | Low |

---

## 5. Query Cookbook

### 5.1 Cost Analysis

```sql
-- Daily cost by service (last 30 days)
SELECT
  DATE(usage_start_time) as date,
  service.description as service,
  ROUND(SUM(cost), 2) as cost
FROM `flash-clover-464719-g1.google_cost_pricing.gcp_billing_export_v1_01A3A4_B9BD05_F12FEE`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY 1, 2
HAVING cost > 0.01
ORDER BY date, cost DESC
```

### 5.2 Security Monitoring

```sql
-- Recent sensitive operations
SELECT
  timestamp,
  protopayload_auditlog.authenticationInfo.principalEmail as actor,
  protopayload_auditlog.methodName as action
FROM `flash-clover-464719-g1.audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND (protopayload_auditlog.methodName LIKE '%Delete%'
       OR protopayload_auditlog.methodName LIKE '%SetIam%')
ORDER BY timestamp DESC
```

### 5.3 Pipeline Cost Attribution

```sql
-- Cost by pipeline (last 7 days)
SELECT
  REGEXP_EXTRACT(operation_type, r'^([a-z_]+)_pipeline') as pipeline,
  COUNT(*) as operations,
  ROUND(SUM(total_cost_usd), 2) as total_cost,
  ROUND(SUM(bytes_read)/1024/1024/1024, 2) as gb_read
FROM `flash-clover-464719-g1.governance.process_costs`
WHERE started_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY 1
ORDER BY total_cost DESC
```

---

## 6. Data Dictionary

### 6.1 Export Datasets

| Dataset | Location | Purpose | Update Frequency |
|---------|----------|---------|------------------|
| `google_cost_pricing` | us-central1 | Billing data | Real-time |
| `audit_logs` | US | Security audit trail | Real-time |
| `recommender_insights` | US | IAM/cost recommendations | On-demand |
| `carbon_footprint` | US | Emissions tracking | Monthly |

### 6.2 Governance Datasets

| Dataset | Purpose | Key Tables |
|---------|---------|------------|
| `governance` | Cost tracking, alerts | `process_costs`, `unified_alerts` |
| `security` | Security monitoring | `iam_security_alerts`, `admin_activity_summary` |
| `cost_monitoring` | Anomaly detection | `cost_anomaly_detection`, `daily_cost_summary` |

### 6.3 Core Services

| Service | File | Purpose |
|---------|------|---------|
| GCPOperationsService | `governance/gcp_operations_service.py` | Unified GCP data access |
| CostAttributionService | `governance/cost_attribution_service.py` | Pipeline cost tracking |
| SecurityPostureMonitor | `governance/security_posture_monitor.py` | IAM/audit analysis |
| Pre-Run Validator | `governance/pre_run_validator.py` | Pre-execution checks |

---

## Appendix: CLI Tool Reference

```bash
# Full operational health report
python tools/operational_health.py

# Cost summary only
python tools/operational_health.py --costs

# Security posture only
python tools/operational_health.py --security

# Unified alerts
python tools/operational_health.py --alerts

# JSON output for automation
python tools/operational_health.py --json
```

---

*This analysis is generated from live GCP export data. Run `python tools/operational_health.py` for the latest status.*
