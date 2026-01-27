# GCP Exports Integration Analysis

**Purpose**: Analyze how GCP BigQuery exports integrate with Truth Engine infrastructure
**Created**: 2025-12-22
**Project**: `flash-clover-464719-g1`

---

## Executive Summary

Your GCP exports provide **three layers of operational intelligence**:

| Layer | Export | Current Data | Integration Status |
|-------|--------|--------------|-------------------|
| **Financial** | Billing + Pricing | $995.32 BigQuery (7 days) | ✅ Integrated via `cost_monitoring.*` |
| **Security** | Audit Logs + Recommender | 16 events, 4 HIGH insights | 🔨 Needs integration |
| **Sustainability** | Carbon Footprint | Awaiting data | 🔨 Needs integration |

---

## Layer 1: Financial Intelligence (Already Working)

### Current State

Your billing exports are already integrated into governance:

```
google_cost_pricing.gcp_billing_export_v1_* → cost_monitoring.daily_cost_summary
                                            → cost_monitoring.cost_anomaly_detection
                                            → cost_monitoring.service_cost_breakdown
                                            → governance.process_costs (enriched)
```

### Key Metrics (Last 7 Days)

| Service | Cost | Line Items |
|---------|------|------------|
| BigQuery | $995.32 | 713 |
| Artifact Registry | $6.55 | 1,139 |
| Gemini API | $2.43 | 27 |
| Compute Engine | $1.89 | 549 |
| Secret Manager | $1.09 | 716 |

**Insight**: BigQuery is 98.7% of costs. The $993.63 incident on Dec 17 visible in these numbers.

### Integration Opportunity: Resource-Level Attribution

Create a view that joins billing to pipeline runs:

```sql
-- Connect BigQuery costs to specific pipeline runs
CREATE OR REPLACE VIEW `cost_monitoring.bigquery_job_costs` AS
SELECT
  r.name as resource_name,
  r.cost,
  r.usage_start_time,
  REGEXP_EXTRACT(r.name, r'bqjob_([a-z0-9]+)_') as job_id,
  p.run_id,
  p.operation_type,
  p.file_path
FROM `google_cost_pricing.gcp_billing_export_resource_v1_01A3A4_B9BD05_F12FEE` r
LEFT JOIN `governance.process_costs` p
  ON REGEXP_EXTRACT(r.name, r'bqjob_([a-z0-9]+)_') = p.cost_id
WHERE r.service.description = 'BigQuery'
  AND r.cost > 0
  AND DATE(r.usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
```

---

## Layer 2: Security Intelligence (New - Needs Integration)

### 2.1 Audit Logs (Real-time)

**Current Data**: 16 events (just enabled, accumulating)

**Tables Available**:
- `audit_logs.cloudaudit_googleapis_com_activity_*` - Admin actions
- `audit_logs.cloudaudit_googleapis_com_data_access_*` - Data access

**Integration Points**:

#### A. Security Dashboard View

```sql
CREATE OR REPLACE VIEW `security.admin_activity_summary` AS
SELECT
  DATE(timestamp) as activity_date,
  protopayload_auditlog.authenticationInfo.principalEmail as actor,
  protopayload_auditlog.serviceName as service,
  protopayload_auditlog.methodName as action,
  resource.type as resource_type,
  COUNT(*) as action_count
FROM `audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY 1, 2, 3, 4, 5
ORDER BY activity_date DESC, action_count DESC
```

#### B. Alert Integration with governance.process_costs

```sql
-- Correlate audit events with cost events
CREATE OR REPLACE VIEW `governance.audit_cost_correlation` AS
SELECT
  a.timestamp as audit_time,
  p.started_at as process_time,
  a.protopayload_auditlog.authenticationInfo.principalEmail as actor,
  p.operation_type,
  p.total_cost_usd,
  a.protopayload_auditlog.methodName as audit_action
FROM `audit_logs.cloudaudit_googleapis_com_activity_*` a
JOIN `governance.process_costs` p
  ON DATE(a.timestamp) = DATE(p.started_at)
  AND ABS(TIMESTAMP_DIFF(a.timestamp, p.started_at, MINUTE)) < 5
WHERE a.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

### 2.2 Recommender Insights (Periodic Export)

**Current Data**: 4 HIGH severity insights, 45,085 total permissions identified

| Member | Role | Permissions | Status |
|--------|------|-------------|--------|
| jeremy.serna@gmail.com | roles/owner | 12,371 | 469 used (3.8%) |
| 81233637196-compute@... | roles/editor | 10,914 | 37 used (0.3%) |
| 81233637196@cloudservices... | roles/editor | 10,900 | 0 used |
| flash-clover-464719-g1@appspot... | roles/editor | 10,900 | 1 used |

**Security Risk**: Three service accounts have Editor role but use <1% of permissions.

**Integration Points**:

#### A. Governance Alert View

```sql
CREATE OR REPLACE VIEW `governance.security_alerts` AS
SELECT
  'IAM_OVERPRIVILEGED' as alert_type,
  severity,
  member,
  role,
  permissions_count,
  description,
  exported_at as detected_at
FROM `recommender_insights.iam_policy_insights`
WHERE severity = 'HIGH'
```

#### B. Scheduled Export Enhancement

Update `tools/export_recommender_insights.py` to:
1. Export daily via Cloud Scheduler
2. Add cost recommendations (not just IAM)
3. Track recommendation status over time

---

## Layer 3: Sustainability Intelligence (Pending Console Action)

### Current State

Dataset created: `carbon_footprint`
Export status: **Pending console enablement**

### Once Enabled, Integration Points

#### A. Infrastructure Carbon View

```sql
CREATE OR REPLACE VIEW `infrastructure.carbon_by_service` AS
SELECT
  carbon_footprint_total_kgco2e.service_id,
  SUM(carbon_footprint_total_kgco2e.gross_carbon_footprint_kgco2e) as gross_carbon_kg,
  SUM(carbon_footprint_total_kgco2e.location_based_carbon_footprint_kgco2e) as location_carbon_kg,
  AVG(carbon_footprint_total_kgco2e.carbon_free_energy_percentage) as avg_cfe_pct
FROM `carbon_footprint.carbon_footprint_export`
GROUP BY 1
```

#### B. Carbon-Cost Correlation

```sql
-- Compare carbon and dollar costs
CREATE OR REPLACE VIEW `governance.carbon_cost_ratio` AS
SELECT
  c.service_id,
  c.gross_carbon_kg,
  b.total_cost,
  SAFE_DIVIDE(c.gross_carbon_kg, b.total_cost) as carbon_per_dollar
FROM `infrastructure.carbon_by_service` c
JOIN (
  SELECT service.description as service_id, SUM(cost) as total_cost
  FROM `google_cost_pricing.gcp_billing_export_v1_*`
  GROUP BY 1
) b ON c.service_id = b.service_id
```

---

## Unified Integration Architecture

### Proposed Dataset Structure

```
┌────────────────────────────────────────────────────────────────────┐
│                     GCP EXPORT SOURCES (Raw)                        │
├────────────────────────────────────────────────────────────────────┤
│  google_cost_pricing.*  │  audit_logs.*  │  carbon_footprint.*     │
│  pricing_data.*         │                │  recommender_insights.* │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER (Views)                        │
├────────────────────────────────────────────────────────────────────┤
│  cost_monitoring.*           │ security.*        │ infrastructure.* │
│  ├── daily_cost_summary      │ ├── admin_activity│ ├── carbon_by_svc│
│  ├── cost_anomaly_detection  │ ├── security_alerts│ └── carbon_cost │
│  ├── bigquery_job_costs      │ └── audit_cost_   │     _ratio       │
│  ├── estimated_vs_actual     │     correlation   │                  │
│  └── service_cost_breakdown  │                   │                  │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                    GOVERNANCE LAYER (Enriched)                      │
├────────────────────────────────────────────────────────────────────┤
│  governance.process_costs      │ governance.security_alerts        │
│  governance.audit_cost_corr    │ governance.carbon_attribution     │
│  governance.unified_alerts     │                                   │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                                │
├────────────────────────────────────────────────────────────────────┤
│  Pre-commit hooks              │ Real-time alerts    │ Dashboards  │
│  cost_protection_hook.py       │ Cloud Monitoring    │ Looker      │
│  governance_gate.py            │ PagerDuty/Slack     │ Studio      │
└────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Security Views (Immediate)

```bash
# Create security views
bq query --use_legacy_sql=false '
CREATE SCHEMA IF NOT EXISTS `flash-clover-464719-g1.security`
OPTIONS(location="US", description="Security and audit intelligence")
'
```

### Phase 2: Governance Correlation

```python
# Add to governance/cost_tracking_service.py
def get_audit_cost_correlation(run_id: str) -> dict:
    """Correlate audit events with cost events for a run."""
    query = """
    SELECT a.*, p.total_cost_usd
    FROM `audit_logs.cloudaudit_googleapis_com_activity_*` a
    JOIN `governance.process_costs` p ON ...
    WHERE p.run_id = @run_id
    """
    # ... implementation
```

### Phase 3: Unified Alerts

Create `governance.unified_alerts` view combining:
- Cost anomalies (z-score > 2)
- Security alerts (HIGH severity IAM insights)
- Audit irregularities (unusual access patterns)

---

## Completed Integration (2025-12-22)

### Views Created

| Dataset | View | Purpose |
|---------|------|---------|
| `security` | `admin_activity_summary` | Aggregated admin actions by actor/service/action |
| `security` | `iam_security_alerts` | HIGH severity IAM overprivilege alerts with risk levels |
| `governance` | `unified_alerts` | Combined cost + security alerts in single view |
| `google_cost_pricing` | `bigquery_resource_costs` | Resource-level BigQuery costs aggregated |

### Sample Unified Alerts Output

```
| alert_type         | severity | source                              | description                           |
|--------------------|----------|-------------------------------------|---------------------------------------|
| IAM_OVERPRIVILEGED | CRITICAL | ...@appspot.gserviceaccount.com     | Unused permissions: 10900 (1 used)    |
| IAM_OVERPRIVILEGED | CRITICAL | ...@cloudservices.gserviceaccount   | Unused permissions: 10900 (0 used)    |
| IAM_OVERPRIVILEGED | CRITICAL | jeremy.serna@gmail.com              | Unused permissions: 12371 (469 used)  |
```

### Query Examples

```sql
-- All critical alerts (cost + security combined)
SELECT * FROM `governance.unified_alerts`
WHERE severity IN ('CRITICAL', 'CRITICAL_ANOMALY')

-- Who did what today (audit trail)
SELECT * FROM `security.admin_activity_summary`
WHERE activity_date = CURRENT_DATE()
ORDER BY action_count DESC

-- Top BigQuery resource costs
SELECT * FROM `google_cost_pricing.bigquery_resource_costs`
ORDER BY total_cost DESC LIMIT 20
```

---

## Remaining Actions

### 1. Schedule Recommender Export

```bash
# Add to Cloud Scheduler for daily export
gcloud scheduler jobs create http recommender-daily-export \
  --schedule="0 6 * * *" \
  --uri="https://us-central1-flash-clover-464719-g1.cloudfunctions.net/export-recommender" \
  --http-method=POST \
  --time-zone="America/Los_Angeles"
```

### 3. Enable Carbon Footprint (Console Action Required)

Visit [Carbon Footprint Console](https://console.cloud.google.com/carbon?project=flash-clover-464719-g1) and click "Export to BigQuery".

---

## Value Summary

| Export | Current Value | Potential Value |
|--------|---------------|-----------------|
| **Billing** | Cost tracking, anomaly detection | Resource-level attribution to pipelines |
| **Audit Logs** | Raw event capture | Security posture, incident correlation |
| **Recommender** | IAM insights captured | Automated permission right-sizing |
| **Carbon** | Awaiting data | Sustainability reporting, carbon-aware scheduling |

**Combined Value**: Single source of truth for cost, security, and sustainability - all queryable via SQL, all correlated with pipeline runs.
