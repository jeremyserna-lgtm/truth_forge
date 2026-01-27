# GCP BigQuery Exports - Source of Truth

**Purpose**: Document all available Google Cloud exports to BigQuery for cost tracking, security auditing, and operational insights.
**Project**: `flash-clover-464719-g1`
**Last Updated**: 2025-12-22

---

## Executive Summary

Google Cloud provides several data exports to BigQuery that serve as authoritative sources of truth for billing, security, sustainability, and operational optimization. This document catalogs all available exports, their status, and how they integrate with Truth Engine.

### Current Status (2025-12-22)

| Export | Status | Dataset |
|--------|--------|---------|
| Standard Billing | ✅ Enabled | `google_cost_pricing` |
| Detailed Billing (Resource) | ✅ Enabled | `google_cost_pricing` |
| Cloud Pricing | ✅ Enabled | `pricing_data` |
| Audit Logs | ✅ Enabled | `audit_logs` |
| Carbon Footprint | ⚠️ Console Action Required | `carbon_footprint` |
| Recommender Insights | ✅ Enabled | `recommender_insights` |

---

## Export Catalog

### 1. Billing Exports

#### Standard Billing Export
| Field | Value |
|-------|-------|
| **Status** | ✅ Enabled |
| **Dataset** | `google_cost_pricing` |
| **Table** | `gcp_billing_export_v1_01A3A4_B9BD05_F12FEE` |
| **Update Frequency** | Near real-time (within hours) |
| **Retention** | Indefinite |

**What It Provides:**
- Daily cost breakdown by service
- SKU-level cost details
- Project and label attribution
- Credits and discounts applied

**Use Cases for Truth Engine:**
- Cost anomaly detection (`cost_monitoring.cost_anomaly_detection`)
- Budget tracking and alerts
- Service cost optimization
- Correlation with pipeline runs

**Sample Query:**
```sql
SELECT
  DATE(usage_start_time) as date,
  service.description as service,
  SUM(cost) as total_cost
FROM `flash-clover-464719-g1.google_cost_pricing.gcp_billing_export_v1_01A3A4_B9BD05_F12FEE`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1, 2
ORDER BY total_cost DESC
```

---

#### Detailed Billing Export (Resource-Level)
| Field | Value |
|-------|-------|
| **Status** | ✅ Enabled |
| **Dataset** | `google_cost_pricing` |
| **Table** | `gcp_billing_export_resource_v1_01A3A4_B9BD05_F12FEE` |
| **Update Frequency** | Near real-time |
| **Retention** | Indefinite |

**What It Provides:**
- Resource-level cost attribution (individual VMs, tables, jobs)
- Resource name and type
- Fine-grained usage metrics

**Use Cases for Truth Engine:**
- Identify expensive BigQuery queries
- Track Cloud Run job costs
- Attribute costs to specific pipelines
- Optimize resource allocation

**Sample Query:**
```sql
SELECT
  resource.name,
  service.description,
  SUM(cost) as cost
FROM `flash-clover-464719-g1.google_cost_pricing.gcp_billing_export_resource_v1_01A3A4_B9BD05_F12FEE`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND cost > 0
GROUP BY 1, 2
ORDER BY cost DESC
LIMIT 20
```

---

#### Cloud Pricing Export
| Field | Value |
|-------|-------|
| **Status** | ✅ Enabled |
| **Dataset** | `pricing_data` |
| **Table** | `cloud_pricing_export` |
| **Update Frequency** | Daily |
| **Retention** | Indefinite |

**What It Provides:**
- Current pricing for all GCP SKUs
- Unit pricing and currency
- Pricing tiers and conditions

**Use Cases for Truth Engine:**
- Cost estimation before running jobs
- Budget forecasting
- Price trend analysis
- Optimize SKU selection

---

### 2. Audit Logs Export

| Field | Value |
|-------|-------|
| **Status** | ✅ Enabled (2025-12-22) |
| **Dataset** | `audit_logs` |
| **Table** | `cloudaudit_googleapis_com_*` (auto-created) |
| **Update Frequency** | Real-time |
| **Sink Name** | `audit-logs-to-bigquery` |

**What It Provides:**
- Admin Activity logs (who did what)
- Data Access logs (who accessed what data)
- System Event logs (GCP system actions)
- Policy Denied logs (failed access attempts)

**Use Cases for Truth Engine:**
- Security compliance auditing
- Track who modified resources
- Detect unauthorized access attempts
- Compliance reporting (SOC2, etc.)

**Sample Query:**
```sql
-- Recent admin activity
SELECT
  timestamp,
  protopayload_auditlog.authenticationInfo.principalEmail as actor,
  protopayload_auditlog.methodName as action,
  resource.type as resource_type
FROM `flash-clover-464719-g1.audit_logs.cloudaudit_googleapis_com_activity_*`
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
ORDER BY timestamp DESC
LIMIT 100
```

**Note:** Audit logs start flowing immediately. Initial tables created: `cloudaudit_googleapis_com_activity_*` and `cloudaudit_googleapis_com_data_access_*`.

---

### 3. Carbon Footprint Export

| Field | Value |
|-------|-------|
| **Status** | ⚠️ Dataset Created, Console Action Required |
| **Dataset** | `carbon_footprint` |
| **Table** | `carbon_footprint_export` (pending) |
| **Update Frequency** | Monthly |

**What It Provides:**
- Gross carbon emissions by service
- Carbon-free energy percentage
- Location-based emissions
- Market-based emissions

**Use Cases for Truth Engine:**
- Sustainability reporting
- Carbon-aware scheduling
- Environmental impact tracking
- ESG compliance

---

### 4. Recommender Insights Export

| Field | Value |
|-------|-------|
| **Status** | ✅ Enabled (2025-12-22) |
| **Dataset** | `recommender_insights` |
| **Table** | `iam_policy_insights` |
| **Update Frequency** | On-demand (script) |
| **Export Script** | `tools/export_recommender_insights.py` |

**What It Provides:**
- Cost optimization recommendations
- Security recommendations (IAM)
- Performance recommendations
- Reliability recommendations

**Current Data (as of 2025-12-22):**
- 4 HIGH severity IAM insights exported
- Unused permissions identified
- Service account audit capabilities

**Use Cases for Truth Engine:**
- Automated cost optimization
- Security posture improvement
- Resource right-sizing
- Idle resource cleanup

**Sample Query:**
```sql
SELECT
  severity,
  member,
  role,
  permissions_count,
  description
FROM `flash-clover-464719-g1.recommender_insights.iam_policy_insights`
WHERE severity = 'HIGH'
ORDER BY permissions_count DESC
```

---

## Integration with Truth Engine

### Cost Tracking Integration

The billing exports feed into the cost tracking governance layer:

```
Billing Export → cost_monitoring views → governance.process_costs
                                      → Hook enforcement (CP rules)
                                      → Anomaly detection
```

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP EXPORT SOURCES                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ Billing Exports (Enabled)                               │
│  ├── Standard billing → Daily cost analysis                │
│  ├── Resource billing → Per-query cost attribution         │
│  └── Pricing data → Cost estimation                         │
│                                                              │
│  ✅ Audit Logs (Enabled 2025-12-22)                         │
│  ├── Admin Activity → Who changed what                      │
│  ├── Data Access → Who accessed data                        │
│  └── Policy Denied → Security incidents                     │
│                                                              │
│  ⚠️ Carbon Footprint (Console Action Required)              │
│  └── Monthly emissions → Sustainability tracking            │
│                                                              │
│  ✅ Recommender (Enabled 2025-12-22)                        │
│  └── IAM insights → Security posture                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    TRUTH ENGINE INTEGRATION                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  governance.* ← Audit logs, cost tracking                   │
│  cost_monitoring.* ← Billing analysis views                 │
│  operations.* ← Recommender insights                        │
│  infrastructure.* ← Carbon footprint                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup Commands

### Audit Logs Export (✅ Completed 2025-12-22)

```bash
# Dataset created
bq mk --dataset \
  --description "Cloud Audit Logs export from Cloud Logging" \
  --location US \
  flash-clover-464719-g1:audit_logs

# Logging sink created
gcloud logging sinks create audit-logs-to-bigquery \
  bigquery.googleapis.com/projects/flash-clover-464719-g1/datasets/audit_logs \
  --log-filter='logName:"cloudaudit.googleapis.com"' \
  --project=flash-clover-464719-g1

# IAM permissions granted
gcloud projects add-iam-policy-binding flash-clover-464719-g1 \
  --member="serviceAccount:service-81233637196@gcp-sa-logging.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

### Carbon Footprint Export (⚠️ Action Required)

**Dataset created, but export must be enabled via Cloud Console:**
1. Go to [Carbon Footprint Console](https://console.cloud.google.com/carbon?project=flash-clover-464719-g1)
2. Click "Export to BigQuery"
3. Select dataset: `carbon_footprint`

### Recommender Export (✅ Completed 2025-12-22)

```bash
# Dataset created
bq mk --dataset \
  --description "Recommender insights export" \
  --location US \
  flash-clover-464719-g1:recommender_insights

# Run export script
python tools/export_recommender_insights.py

# Optional: Schedule daily export via Cloud Scheduler
gcloud scheduler jobs create http recommender-export \
  --schedule="0 6 * * *" \
  --uri="https://us-central1-flash-clover-464719-g1.cloudfunctions.net/export-recommender" \
  --http-method=POST
```

---

## Monitoring and Alerts

### Cost Anomaly Detection

The `cost_monitoring` dataset contains views for detecting anomalies:

| View | Purpose |
|------|---------|
| `daily_cost_summary` | Daily cost totals by service |
| `cost_anomaly_detection` | Identifies unusual cost patterns |
| `service_cost_breakdown` | Detailed service-level costs |
| `realtime_alerts` | Triggers for budget thresholds |
| `estimated_vs_actual` | Compares estimates to actuals |

### Alert Integration

```sql
-- Example: Alert on daily cost spike > 50%
SELECT
  date,
  total_cost,
  LAG(total_cost) OVER (ORDER BY date) as prev_cost,
  (total_cost - LAG(total_cost) OVER (ORDER BY date)) /
    NULLIF(LAG(total_cost) OVER (ORDER BY date), 0) * 100 as pct_change
FROM `flash-clover-464719-g1.cost_monitoring.daily_cost_summary`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
HAVING pct_change > 50
```

---

## Related Documents

- [COMPREHENSIVE_HOOK_ARCHITECTURE.md](COMPREHENSIVE_HOOK_ARCHITECTURE.md) - Cost protection hooks
- [COST_OVERRUN_PREVENTION_REQUIREMENTS.md](COST_OVERRUN_PREVENTION_REQUIREMENTS.md) - Cost controls
- [cost_tracking_service.py](../architect_central_services/src/architect_central_services/governance/cost_tracking_service.py) - Cost tracking implementation
