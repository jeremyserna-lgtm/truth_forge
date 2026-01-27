# Google Cloud BigQuery Exports - Complete Reference

**Purpose**: Comprehensive catalog of all Google Cloud data exports to BigQuery available to cloud users.
**Last Updated**: 2025-12-22
**Maintainer**: Truth Engine

---

## Executive Summary

Google Cloud provides multiple data export mechanisms to BigQuery, enabling centralized analysis of billing, operations, security, and asset data. This document catalogs all available exports with their setup status for the Truth Engine project.

---

## 1. Cloud Billing Exports

### 1.1 Standard Usage Cost Data
**Table Name**: `gcp_billing_export_v1_<BILLING_ACCOUNT_ID>`
**Status**: ✅ ENABLED
**Current Data**: 45,891 rows (Oct 31 - Dec 22, 2025)

Contains high-level billing information:
- Account ID, invoice date
- Services, SKUs, projects
- Labels, locations
- Cost, usage, credits, adjustments, currency

**Use Case**: Analyze broad trends in cost data.

### 1.2 Detailed Usage Cost Data (Resource-Level)
**Table Name**: `gcp_billing_export_resource_v1_<BILLING_ACCOUNT_ID>`
**Status**: ✅ ENABLED
**Current Data**: 333,956 rows (Oct 31 - Dec 22, 2025)

Everything in standard export PLUS:
- Resource-level cost data (VMs, SSDs, etc.)
- Resource names and IDs
- System labels (after Sept 17, 2025)

**Use Case**: Track costs at resource level, identify cost drivers.

### 1.3 Pricing Data Export
**Table Name**: `cloud_pricing_export`
**Status**: ❌ NOT ENABLED

Contains:
- SKU pricing structures
- Pricing tiers
- Contract details
- Public vs. negotiated pricing

**Use Case**: Join with cost data for detailed pricing analysis.

**Setup Required**: Enable in Cloud Billing Console → Billing Export → Pricing data.

### 1.4 Committed Use Discounts (CUD) Metadata
**Table Name**: `cud_subscriptions_export`
**Status**: ❌ NOT ENABLED (Preview)

Contains:
- Billing account ID
- Product ID, consumption model ID
- Commitment amounts and values

**Use Case**: CUD management and reporting.

---

## 2. Cloud Logging Exports

### 2.1 Log Router Sink to BigQuery
**Status**: ❌ NOT CONFIGURED

Current logging sinks route only to Cloud Logging buckets:
- `_Required`: Audit logs
- `_Default`: All other logs

**What Can Be Exported**:
- Admin Activity audit logs
- Data Access audit logs
- System Event audit logs
- Application logs (Cloud Run, GKE, etc.)
- VPC Flow logs
- Firewall Rules logs

**Setup Required**: Create a new sink in Log Router with BigQuery destination.

### 2.2 Log Analytics (Linked Dataset)
**Status**: ❌ NOT CONFIGURED

Alternative approach:
1. Upgrade log bucket to Log Analytics
2. Create linked BigQuery dataset
3. Query logs directly via BigQuery

**Recommended by Google** for log analysis.

---

## 3. Cloud Asset Inventory Exports

### 3.1 Asset Snapshot Export
**Table Name**: User-defined
**Status**: ❌ NOT CONFIGURED
**API**: Cloud Asset API (✅ ENABLED)

Exports:
- All GCP resources across org/folder/project
- Resource metadata, IAM policies
- Organization policies
- Access policies

**Export Types**:
- One-time snapshot
- Per-asset-type tables (separate table per resource type)

### 3.2 Asset Change Feed
**Status**: ❌ NOT CONFIGURED

Continuous monitoring:
- Subscribe to asset change notifications
- Route to Pub/Sub → BigQuery

---

## 4. Recommender Exports

### 4.1 Recommendations Export
**Table Name**: User-defined via Data Transfer Service
**Status**: ❌ NOT CONFIGURED

Daily snapshots of:
- Cost recommendations (right-sizing, idle resources)
- Security recommendations
- Performance recommendations
- Reliability recommendations
- Sustainability recommendations

**Features**:
- Supports negotiated pricing for cost savings calculations
- Exports at organization, folder, project, billing account levels

---

## 5. Security Command Center Exports

### 5.1 Findings Export to BigQuery
**Table Name**: User-defined
**Status**: ❌ NOT CONFIGURED

Exports:
- Security findings (vulnerabilities, threats)
- Compliance findings
- Asset data (deprecated - use Cloud Asset Inventory)

**Export Types**:
- One-time bulk export
- Continuous export via Pub/Sub

**Note**: Requires SCC Premium or Enterprise tier.

---

## 6. Monitoring Metrics Export

### 6.1 Cloud Monitoring Metrics to BigQuery
**Status**: ❌ NOT CONFIGURED

Export options:
- Custom metrics export via API
- Third-party integration (Datadog, etc.)

**Recommendation**: Aggregate at 1-hour minimum granularity.

### 6.2 BigQuery INFORMATION_SCHEMA
**Status**: ✅ BUILT-IN

Query metadata about:
- Jobs (JOBS_BY_*, JOBS_TIMELINE_BY_*)
- Tables (TABLES, TABLE_STORAGE)
- Datasets, routines, views
- Streaming stats

---

## 7. Other Data Sources

### 7.1 Google Analytics 4 Export
**Status**: N/A (Not applicable for this project)

### 7.2 Firebase Performance Monitoring Export
**Status**: N/A

### 7.3 Google Workspace Audit Logs Export
**Status**: ❌ NOT CONFIGURED (if using Workspace)

---

## Current Status Summary

| Export Type | Table Exists | Data Flowing | Priority |
|-------------|--------------|--------------|----------|
| Standard Billing | ✅ | ✅ 45,891 rows | - |
| Detailed Billing | ✅ | ✅ 333,956 rows | - |
| Pricing Data | ❌ | ❌ | HIGH |
| CUD Metadata | ❌ | ❌ | LOW |
| Cloud Logging | ❌ | ❌ | HIGH |
| Asset Inventory | ❌ | ❌ | MEDIUM |
| Recommender | ❌ | ❌ | MEDIUM |
| Security Center | ❌ | ❌ | LOW |
| Monitoring Metrics | ❌ | ❌ | LOW |

---

## Recommended Actions

### Priority 1: Enable Pricing Data Export
```
Console: Billing → Billing Export → Pricing data → Enable
```
Enables joining pricing with costs for margin analysis.

### Priority 2: Create Cloud Logging Sink to BigQuery
```bash
gcloud logging sinks create truth-engine-logs \
  bigquery.googleapis.com/projects/flash-clover-464719-g1/datasets/cloud_logs \
  --log-filter='severity>=WARNING'
```
Captures errors and warnings for operational analysis.

### Priority 3: Enable Recommender Export
```
Console: Recommender → BigQuery Export → Configure
```
Provides daily recommendations for cost optimization.

### Priority 4: Schedule Asset Inventory Export
```bash
gcloud asset export \
  --organization=YOUR_ORG_ID \
  --bigquery-table=flash-clover-464719-g1.assets.inventory \
  --content-type=resource
```
Creates asset snapshot for governance.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Cloud Billing │  Cloud Logging  │     Cloud Operations        │
│   ┌───────────┐ │  ┌───────────┐  │  ┌───────────┐ ┌─────────┐  │
│   │ Standard  │ │  │ Log Sink  │  │  │ Recomm.   │ │ Metrics │  │
│   │ Detailed  │ │  │   (TBD)   │  │  │   (TBD)   │ │  (TBD)  │  │
│   │ Pricing * │ │  │           │  │  │           │ │         │  │
│   └─────┬─────┘ │  └─────┬─────┘  │  └─────┬─────┘ └────┬────┘  │
└─────────┼───────┴────────┼────────┴────────┼────────────┼───────┘
          │                │                 │            │
          ▼                ▼                 ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BigQuery                                 │
├─────────────────────────────────────────────────────────────────┤
│  google_cost_pricing/    cloud_logs/      recommender/          │
│  ├─ billing_v1 ✅        (to create)      (to create)           │
│  ├─ billing_resource ✅                                         │
│  └─ pricing (TBD)                                               │
└─────────────────────────────────────────────────────────────────┘

* = Not yet enabled
TBD = To be configured
```

---

## Sources

- [Export Cloud Billing data to BigQuery](https://cloud.google.com/billing/docs/how-to/export-data-bigquery)
- [Structure of Detailed data export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/detailed-usage)
- [Route logs to BigQuery](https://cloud.google.com/logging/docs/export/configure_export_v2)
- [View logs routed to BigQuery](https://cloud.google.com/logging/docs/export/bigquery)
- [Export asset metadata to BigQuery](https://cloud.google.com/asset-inventory/docs/export-bigquery)
- [Export recommendations to BigQuery](https://cloud.google.com/recommender/docs/bq-export/export-recommendations-to-bq)
- [Export Security Command Center data](https://cloud.google.com/security-command-center/docs/how-to-export-data)

---

## Related Documents

- [01-cost-protection.md](.claude/rules/01-cost-protection.md) - Cost control rules
- [central_config.toml](architect_central_services/central_config.toml) - BigQuery configuration
