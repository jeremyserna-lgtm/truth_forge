# Credential Atlas Data Mapping & Ingestion Plan

**Date**: January 6, 2026
**Purpose**: Map all data sources and prepare ingestion pipelines for Credential Atlas

---

## 🎯 DATA OVERVIEW

**Total Records**: 600,000+ across 8 core tables
**Data Sources**: IPEDS, College Scorecard, BLS, Credential Engine, State Registries
**Storage**: BigQuery (production), DuckDB (local development)
**Pattern**: HOLD → AGENT → HOLD (Framework pattern)

---

## 📊 CORE TABLES (8 Tables)

### 1. `ipeds_completions` (303k records)
**Source**: IPEDS (Integrated Postsecondary Education Data System)
**Purpose**: Institutional completion data by program
**Key Fields**: Institution ID, Program CIP code, Completion counts, Demographics

### 2. `scorecard_programs` (213k records)
**Source**: College Scorecard
**Purpose**: Program-level outcomes and earnings data
**Key Fields**: Program name, Earnings, Debt, Completion rates

### 3. `bls_occupation_wages` (34k records)
**Source**: Bureau of Labor Statistics (BLS)
**Purpose**: Occupation wage and employment data
**Key Fields**: Occupation code (SOC), Median wage, Employment counts, Geographic data

### 4. `national_credentials` (8k generated records)
**Source**: Credential Engine Registry + Generated
**Purpose**: National credential registry data
**Key Fields**: Credential ID, Name, Type, Issuer, CTDL alignment

### 5. `institutions` (Estimated 4k+ records)
**Source**: IPEDS + College Scorecard
**Purpose**: Institution master data
**Key Fields**: Institution ID, Name, Type, Location, Characteristics

### 6. `programs` (Estimated 200k+ records)
**Source**: IPEDS + Scorecard
**Purpose**: Program master data
**Key Fields**: Program ID, CIP code, Name, Level, Institution link

### 7. `occupations` (Estimated 800+ records)
**Source**: BLS Standard Occupational Classification (SOC)
**Purpose**: Occupation master data
**Key Fields**: SOC code, Title, Category, Description

### 8. `credential_occupation_mappings` (Estimated 50k+ records)
**Source**: Generated/Enriched
**Purpose**: Links credentials to occupations
**Key Fields**: Credential ID, Occupation SOC, Confidence score, Source

---

## 🔄 DATA FLOW (HOLD → AGENT → HOLD)

### Pattern for Each Data Source

```
RAW DATA (External Source)
    │
    ▼
HOLD₁: staging/{source}/intake/raw.jsonl
    │
    ▼
AGENT: scripts/ingest/{source}_ingest.py
    │
    ▼
HOLD₂: staging/{source}/processed/cleaned.jsonl
    │
    ▼
AGENT: scripts/ingest/sync_to_bigquery.py
    │
    ▼
HOLD₃: BigQuery Table (flash-clover-464719-g1.credential_atlas.{table_name})
```

---

## 📋 DATA SOURCE DETAILS

### Source 1: IPEDS (Institutional Data)

**What It Is**: Federal data on postsecondary institutions
**Update Frequency**: Annual
**Data Types**:
- Institution characteristics
- Completions by program
- Enrollment data
- Financial data

**Tables**:
- `ipeds_completions` (303k records)
- `institutions` (derived)

**Ingestion Script**: `scripts/ingest/ipeds_ingest.py`

---

### Source 2: College Scorecard

**What It Is**: Program-level outcomes and earnings
**Update Frequency**: Annual
**Data Types**:
- Program earnings
- Debt outcomes
- Completion rates
- Student demographics

**Tables**:
- `scorecard_programs` (213k records)
- `programs` (derived)

**Ingestion Script**: `scripts/ingest/scorecard_ingest.py`

---

### Source 3: BLS (Bureau of Labor Statistics)

**What It Is**: Occupation wage and employment data
**Update Frequency**: Annual
**Data Types**:
- Occupation wages (median, percentiles)
- Employment counts
- Geographic data
- Projected growth

**Tables**:
- `bls_occupation_wages` (34k records)
- `occupations` (derived)

**Ingestion Script**: `scripts/ingest/bls_ingest.py`

---

### Source 4: Credential Engine Registry

**What It Is**: National credential registry (CTDL standard)
**Update Frequency**: Continuous (API)
**Data Types**:
- Credential definitions
- Issuer information
- CTDL metadata
- Credential types

**Tables**:
- `national_credentials` (8k records, growing)

**Ingestion Script**: `scripts/ingest/credential_engine_ingest.py`

---

### Source 5: State Registries (Future)

**What It Is**: State-specific credential registries
**Update Frequency**: Varies by state
**Data Types**:
- State-licensed credentials
- Workforce credentials
- Apprenticeship programs

**Tables**:
- `state_credentials` (future)

**Ingestion Script**: `scripts/ingest/state_registry_ingest.py` (future)

---

## 🗄️ BIGQUERY SCHEMA DEFINITIONS

### Table 1: `ipeds_completions`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.ipeds_completions` (
    completion_id STRING NOT NULL,
    institution_id STRING NOT NULL,
    cip_code STRING,
    award_level STRING,
    completion_count INTEGER,
    demographic_category STRING,
    academic_year STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY institution_id, cip_code;
```

---

### Table 2: `scorecard_programs`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.scorecard_programs` (
    program_id STRING NOT NULL,
    institution_id STRING NOT NULL,
    program_name STRING,
    cip_code STRING,
    credential_level STRING,
    median_earnings_10_yrs NUMERIC,
    median_debt NUMERIC,
    completion_rate NUMERIC,
    academic_year STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY institution_id, cip_code;
```

---

### Table 3: `bls_occupation_wages`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.bls_occupation_wages` (
    wage_id STRING NOT NULL,
    soc_code STRING NOT NULL,
    occupation_title STRING,
    median_wage NUMERIC,
    p10_wage NUMERIC,
    p90_wage NUMERIC,
    employment_count INTEGER,
    geographic_area STRING,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY year
CLUSTER BY soc_code, geographic_area;
```

---

### Table 4: `national_credentials`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.national_credentials` (
    credential_id STRING NOT NULL,
    credential_name STRING NOT NULL,
    credential_type STRING,
    issuer_name STRING,
    issuer_type STRING,
    ctdl_id STRING,
    description STRING,
    industry STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY credential_type, issuer_type;
```

---

### Table 5: `institutions`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.institutions` (
    institution_id STRING NOT NULL,
    institution_name STRING NOT NULL,
    institution_type STRING,
    control_type STRING,
    city STRING,
    state STRING,
    zip_code STRING,
    latitude NUMERIC,
    longitude NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
CLUSTER BY state, institution_type;
```

---

### Table 6: `programs`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.programs` (
    program_id STRING NOT NULL,
    institution_id STRING NOT NULL,
    program_name STRING,
    cip_code STRING,
    credential_level STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY institution_id, cip_code;
```

---

### Table 7: `occupations`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.occupations` (
    occupation_id STRING NOT NULL,
    soc_code STRING NOT NULL,
    occupation_title STRING NOT NULL,
    occupation_category STRING,
    description STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
CLUSTER BY soc_code, occupation_category;
```

---

### Table 8: `credential_occupation_mappings`

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.credential_atlas.credential_occupation_mappings` (
    mapping_id STRING NOT NULL,
    credential_id STRING NOT NULL,
    occupation_soc_code STRING NOT NULL,
    confidence_score NUMERIC,
    mapping_source STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY credential_id, occupation_soc_code;
```

---

## 🔧 INGESTION PIPELINE SCRIPTS

### Script Structure (HOLD → AGENT → HOLD)

Each ingestion script follows this pattern:

```python
# HOLD₁: Read raw data
raw_data = read_from_source()

# AGENT: Transform and clean
cleaned_data = transform_data(raw_data)

# HOLD₂: Write to staging
write_to_staging(cleaned_data, "staging/{source}/processed/cleaned.jsonl")

# AGENT: Sync to BigQuery
sync_to_bigquery(cleaned_data, table_name)

# HOLD₃: BigQuery table (final)
```

---

## ✅ DATA VALIDATION & QUALITY CHECKS

### Validation Rules

1. **Schema Validation**: All fields match schema
2. **Required Fields**: All NOT NULL fields present
3. **Data Types**: Correct types (STRING, NUMERIC, INTEGER, TIMESTAMP)
4. **Referential Integrity**: Foreign keys valid
5. **Uniqueness**: Primary keys unique
6. **Completeness**: No missing critical data
7. **Accuracy**: Data within expected ranges

### Quality Checks

- Record counts match source
- No duplicate records
- Timestamps valid
- Geographic data valid (state codes, zip codes)
- Numeric data within ranges (wages, counts)
- String data not empty where required

---

## 🚀 INGESTION WORKFLOW

### Step 1: Prepare Data Sources
- Download/access raw data
- Validate source data format
- Check for updates

### Step 2: Ingest to Staging (HOLD₁ → AGENT → HOLD₂)
- Run ingestion script
- Transform and clean data
- Write to staging JSONL

### Step 3: Validate Staging Data
- Run validation checks
- Fix any issues
- Verify data quality

### Step 4: Sync to BigQuery (HOLD₂ → AGENT → HOLD₃)
- Run sync script
- Load to BigQuery tables
- Verify load success

### Step 5: Post-Load Validation
- Verify record counts
- Check data quality
- Update metadata

---

## 📁 FILE STRUCTURE

```
scripts/ingest/
├── ipeds_ingest.py
├── scorecard_ingest.py
├── bls_ingest.py
├── credential_engine_ingest.py
├── state_registry_ingest.py (future)
├── sync_to_bigquery.py
└── validate_data.py

staging/
├── ipeds/
│   ├── intake/raw.jsonl
│   └── processed/cleaned.jsonl
├── scorecard/
│   ├── intake/raw.jsonl
│   └── processed/cleaned.jsonl
├── bls/
│   ├── intake/raw.jsonl
│   └── processed/cleaned.jsonl
└── credential_engine/
    ├── intake/raw.jsonl
    └── processed/cleaned.jsonl

docs/schema/credential_atlas/
├── ipeds_completions.yaml
├── scorecard_programs.yaml
├── bls_occupation_wages.yaml
├── national_credentials.yaml
├── institutions.yaml
├── programs.yaml
├── occupations.yaml
└── credential_occupation_mappings.yaml
```

---

## 🎯 NEXT STEPS

1. ✅ **Create schema definitions** (YAML format)
2. ✅ **Create ingestion scripts** (Python, HOLD → AGENT → HOLD pattern)
3. ✅ **Create validation scripts** (Data quality checks)
4. ✅ **Create sync script** (Staging → BigQuery)
5. ✅ **Test ingestion pipeline** (End-to-end test)
6. ✅ **Document data sources** (Source details, update frequency)

---

*Data mapping complete. Ready for ingestion pipeline implementation.*
