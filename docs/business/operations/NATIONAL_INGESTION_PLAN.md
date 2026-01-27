# National Credential Data Ingestion Plan

## Phase 2: IPEDS Institution & Program Enrichment ✅
## Phase 3: Outcomes Enrichment (College Scorecard + BLS) ✅

**Document Version:** 2.0
**Created:** December 14, 2025
**Updated:** December 15, 2025
**Author:** Credential Atlas
**Status:** ✅ Implementation Complete

---

## Complete Data Context Summary

This document provides **complete field-level documentation** for all data sources used in national credential ingestion.

| Table | Fields | Records | Documentation Status |
|-------|--------|---------|---------------------|
| `ipeds_institutions` | 75 | 6,163 | ✅ Complete |
| `ipeds_completions` | 36 | 303,292 | ✅ Complete |
| `ipeds_characteristics` | 45 | 6,049 | ✅ Complete |
| `scorecard_programs` | 44 | 213,711 | ✅ Complete |
| `bls_occupation_wages` | 18 | 34,525 | ✅ **Loaded** |
| `cip_soc_crosswalk` | 11 | 6,097 | ✅ **Loaded** |
| `national_credentials` | 27 | 7,955 | ✅ **Generated** |

**Total Fields Documented:** 256

---

## Executive Summary

This document details the complete implementation plan for building a national credential database from federal data sources. The goal is to create a unified, CTDL-aligned credential repository that serves as the foundation for all credential data alignment, including future Credential Engine integration.

### Current State (December 15, 2025)

| Source | Records | States | Status |
|--------|---------|--------|--------|
| IPEDS Institutions | 6,163 | 59 | ✅ Loaded |
| IPEDS Completions | 303,292 | All | ✅ Loaded |
| IPEDS Characteristics | 6,049 | All | ✅ Loaded |
| College Scorecard Programs | 213,711 | 59 | ✅ Loaded |
| BLS Occupation Wages | 34,525 | 52 | ✅ **Loaded** |
| CIP-SOC Crosswalk | 6,097 | N/A | ✅ **Expanded** |
| **National Credentials** | **7,955** | **All** | ✅ **Generated** |

### Implementation Complete

The unified `national_credentials` table now contains:
- **7,955 credential records** aggregated from IPEDS completions
- **1,560 unique CIP codes** across **12 credential levels**
- **10.8 million total completions** tracked nationally
- **93% wage coverage** via CIP-SOC-BLS linkage (7,420 records)
- **44% Scorecard coverage** with earnings data (3,465 records)
- Connected to **868 occupations** via CIP-SOC crosswalk

### Enterprise Scripts Created

| Script | Purpose | Records |
|--------|---------|---------|
| `scripts/load_bls_wages.py` | BLS OEWS wage data loader | 34,525 |
| `scripts/load_cip_soc_crosswalk.py` | NCES CIP-SOC crosswalk loader | 6,097 |
| `scripts/generate_national_credentials.py` | National credentials generator | 7,955 |

**Script Features:**
- Custom exception hierarchies
- Input/output validation with data quality checks
- Retry logic with exponential backoff (tenacity)
- Structured logging with context (structlog)
- Audit trail via governance module
- Idempotency via `--mode` flag (replace/append)
- Data verification after load

### Views Created

| View | Purpose |
|------|---------|
| `v_national_credentials_scorecard` | Credentials + Scorecard earnings |
| `v_credential_occupations` | Credential → SOC → BLS wage mapping |

---

## Part 1: Complete Data Context Reference

### 1.1 IPEDS Institutions (`ipeds_institutions`)

**Records:** 6,163 | **Primary Key:** `unitid`

#### Core Identity Fields
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `unitid` | STRING | IPEDS Unit ID (6-digit) | Primary key, links to all IPEDS tables |
| `opeid` | STRING | OPE ID (8-digit) | Links to Department of Ed, Title IV eligibility |
| `instnm` | STRING | Institution name | Display name |
| `ialias` | STRING | Institution aliases | Alternative names for matching |
| `ein` | STRING | Employer ID Number | IRS identifier |
| `ueis` | STRING | Unique Entity ID | SAM.gov identifier |

#### Location Fields
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `addr` | STRING | Street address | Full address |
| `city` | STRING | City | Location filtering |
| `stabbr` | STRING | State abbreviation | State-level analysis |
| `zip` | STRING | ZIP code | Geographic targeting |
| `fips` | STRING | FIPS state code | Federal data linkage |
| `countycd` | STRING | County code | Local analysis |
| `countynm` | STRING | County name | Display |
| `cbsa` | STRING | Core-Based Statistical Area | Metro area |
| `cbsatype` | INTEGER | Metro (1) or Micro (2) | Urban/rural classification |
| `csa` | STRING | Combined Statistical Area | Regional analysis |
| `cngdstcd` | STRING | Congressional district | Policy analysis |
| `longitud` | FLOAT | Longitude | Mapping |
| `latitude` | FLOAT | Latitude | Mapping |
| `locale` | INTEGER | Locale code (1-43) | Urban/rural classification |

#### Classification Fields
| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `sector` | INTEGER | Sector | 0=Administrative, 1-9=Educational sectors |
| `iclevel` | INTEGER | Level of institution | 1=4-year, 2=2-year, 3=Less than 2-year |
| `control` | INTEGER | Control | 1=Public, 2=Private nonprofit, 3=Private for-profit |
| `hloffer` | INTEGER | Highest level offered | 1-9 (Certificate to Doctorate) |
| `ugoffer` | INTEGER | Undergraduate offered | 1=Yes, 2=No |
| `groffer` | INTEGER | Graduate offered | 1=Yes, 2=No |
| `hdegofr1` | INTEGER | Highest degree offered | 0-4 |
| `deggrant` | INTEGER | Degree granting | 1=Yes, 2=No |
| `instsize` | INTEGER | Institution size | 1-5 (Under 1K to 20K+) |

#### Special Designations
| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `hbcu` | INTEGER | HBCU status | 1=Yes, 2=No |
| `tribal` | INTEGER | Tribal college | 1=Yes, 2=No |
| `hospital` | INTEGER | Has hospital | 1=Yes, 2=No |
| `medical` | INTEGER | Medical school | 1=Yes, 2=No |
| `landgrnt` | INTEGER | Land grant | 1=Yes, 2=No |
| `openpubl` | INTEGER | Open to public | 1=Yes, 2=No |

#### Carnegie Classification
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `c21basic` | INTEGER | 2021 Basic classification | Current Carnegie |
| `c18basic` | INTEGER | 2018 Basic classification | Historical |
| `c15basic` | INTEGER | 2015 Basic classification | Historical |
| `ccbasic` | INTEGER | Carnegie basic | Legacy |
| `c21ipug` | INTEGER | 2021 Undergrad profile | Student composition |
| `c21ipgrd` | INTEGER | 2021 Graduate profile | Graduate composition |
| `c21ugprf` | INTEGER | 2021 Undergrad program | Program focus |
| `c21enprf` | INTEGER | 2021 Enrollment profile | Enrollment patterns |
| `c21szset` | INTEGER | 2021 Size and setting | Campus type |

#### System Membership
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `f1systyp` | INTEGER | System type | Multi-campus indicator |
| `f1sysnam` | STRING | System name | University system grouping |
| `f1syscod` | STRING | System code | System identifier |

#### URLs
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `webaddr` | STRING | Main website | Institution homepage |
| `adminurl` | STRING | Admissions URL | Application info |
| `faidurl` | STRING | Financial aid URL | Aid info |
| `applurl` | STRING | Application URL | Apply link |
| `npricurl` | STRING | Net price calculator | Cost estimation |
| `veturl` | STRING | Veteran services URL | Veteran info |
| `athurl` | STRING | Athletics URL | Sports info |
| `disaurl` | STRING | Disability services URL | Accessibility |

#### Status Fields
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `act` | STRING | Activity status | Current/inactive |
| `cyactive` | INTEGER | Current year active | 1=Active |
| `postsec` | INTEGER | Postsecondary | 1=Yes |
| `pseflag` | INTEGER | PSE reporting flag | Data availability |
| `pset4flg` | INTEGER | Title IV flag | Financial aid eligible |
| `closedat` | STRING | Closure date | Closed institutions |
| `deathyr` | STRING | Year closed | Historical |
| `newid` | STRING | New UNITID if merged | Institution mergers |

#### Contact Information
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `chfnm` | STRING | Chief administrator name | Contact info |
| `chftitle` | STRING | Chief administrator title | Contact info |
| `gentele` | STRING | General telephone | Phone number |

#### Regional & Regulatory
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `obereg` | STRING | Bureau of Economic Analysis region | Regional analysis |
| `opeflag` | INTEGER | OPE ID status flag | Title IV status |
| `rptmth` | INTEGER | Reporting month | Data timing |
| `instcat` | INTEGER | Institution category | Classification |
| `carnegie` | INTEGER | Legacy Carnegie classification | Historical |
| `dfrcgid` | STRING | Data Feedback Report CG ID | Reporting |
| `dfrcuscg` | STRING | Data Feedback Report USCG | Reporting |

#### Metadata
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `data_year` | INTEGER | IPEDS survey year | Temporal alignment |
| `ingested_at` | TIMESTAMP | When record was loaded | Data freshness |

---

### 1.2 IPEDS Completions (`ipeds_completions`)

**Records:** 303,292 | **Primary Key:** `unitid` + `cipcode` + `awlevel`

#### Core Fields
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `unitid` | STRING | Institution ID | Links to institutions |
| `cipcode` | STRING | CIP code (XX.XXXX) | Program classification |
| `awlevel` | INTEGER | Award level | Credential type |
| `majornum` | INTEGER | Major number | 1=First major, 2=Second major |

#### Award Level Mapping
| Value | Description | CTDL Equivalent |
|-------|-------------|-----------------|
| 1 | Award < 1 academic year | ceterms:Certificate |
| 2 | Award 1-2 academic years | ceterms:Certificate |
| 3 | Associate's degree | ceterms:AssociateDegree |
| 4 | Award 2-4 academic years | ceterms:Certificate |
| 5 | Bachelor's degree | ceterms:BachelorDegree |
| 6 | Postbaccalaureate certificate | ceterms:Certificate |
| 7 | Master's degree | ceterms:MasterDegree |
| 8 | Post-master's certificate | ceterms:Certificate |
| 9 | Doctor's - Research/Scholarship | ceterms:ResearchDoctorate |
| 10 | Doctor's - Professional Practice | ceterms:ProfessionalDoctorate |
| 11 | Doctor's - Other | ceterms:DoctoralDegree |
| 12 | Other award | ceterms:Certificate |

#### Completion Counts (Total)
| Field | Type | Description |
|-------|------|-------------|
| `ctotalt` | INTEGER | Total completions |
| `ctotalm` | INTEGER | Male completions |
| `ctotalw` | INTEGER | Female completions |

#### Completion Counts by Race/Ethnicity
| Field | Description |
|-------|-------------|
| `caiant` / `caianm` / `caianw` | American Indian/Alaska Native (Total/Male/Female) |
| `casiat` / `casiam` / `casiaw` | Asian (Total/Male/Female) |
| `cbkaat` / `cbkaam` / `cbkaaw` | Black/African American (Total/Male/Female) |
| `chispt` / `chispm` / `chispw` | Hispanic/Latino (Total/Male/Female) |
| `cnhpit` / `cnhpim` / `cnhpiw` | Native Hawaiian/Pacific Islander (Total/Male/Female) |
| `cwhitt` / `cwhitm` / `cwhitw` | White (Total/Male/Female) |
| `c2mort` / `c2morm` / `c2morw` | Two or More Races (Total/Male/Female) |
| `cunknt` / `cunknm` / `cunknw` | Unknown (Total/Male/Female) |
| `cnralt` / `cnralm` / `cnralw` | Non-Resident Alien (Total/Male/Female) |

---

### 1.3 IPEDS Characteristics (`ipeds_characteristics`)

**Records:** ~6,000 | **Primary Key:** `unitid`

#### Award Levels Offered
| Field | Description |
|-------|-------------|
| `level1` | Award < 1 year offered |
| `level1a` | Award < 300 clock hours |
| `level1b` | Award 300-899 clock hours |
| `level2` | Award 1-2 years offered |
| `level3` | Associate's offered |
| `level4` | Award 2-4 years offered |
| `level5` | Bachelor's offered |
| `level6` | Postbaccalaureate offered |
| `level7` | Master's offered |
| `level8` | Post-master's offered |
| `level12` | Doctor's - Research |
| `level17` | Doctor's - Professional |
| `level18` | Doctor's - Other |
| `level19` | Graduate certificates |

#### Enrollment Context
| Field | Description |
|-------|-------------|
| `ft_ug` | Full-time undergrad programs |
| `ft_ftug` | Full-time first-time undergrad |
| `ftgdnidp` | Full-time graduate non-degree |
| `pt_ug` | Part-time undergrad |
| `pt_ftug` | Part-time first-time undergrad |
| `ptgdnidp` | Part-time graduate non-degree |
| `openadmp` | Open admission policy |
| `calsys` | Calendar system |

#### Non-Credit Programs
| Field | Description |
|-------|-------------|
| `noncrdt1` | Remedial services |
| `noncrdt2` | Academic/career counseling |
| `noncrdt3` | Employment services for students |
| `noncrdt4` | Placement services for completers |
| `noncrdt5` | On-campus day care |
| `noncrdt6` | Continuing education |
| `noncrdt7` | Weekend/evening programs |
| `noncrdt8` | Distance education |
| `noncrdt9` | ROTC |

#### Doctoral Programs
| Field | Description |
|-------|-------------|
| `docpp` | Doctor's degree - professional practice programs |
| `docppsp` | Doctor's degree - professional practice specialties |

#### High School Enrollment
| Field | Description |
|-------|-------------|
| `enrhsst` | High school students enrolled |
| `enrhsst1` | High school students - regular enrollment |
| `enrhsst2` | High school students - dual enrollment |

#### Veteran Services
| Field | Description |
|-------|-------------|
| `vet1` | Veteran services - credit for military training |
| `vet2` | Veteran services - dedicated veteran support |

#### Affiliation
| Field | Description |
|-------|-------------|
| `cntlaffi` | Control affiliation |
| `pubprime` | Primary public control source |
| `pubsecon` | Secondary public control source |
| `relaffil` | Religious affiliation code |

#### Metadata
| Field | Description |
|-------|-------------|
| `data_year` | IPEDS survey year |
| `ingested_at` | When record was loaded |

---

### 1.4 College Scorecard Programs (`scorecard_programs`)

**Records:** 213,711 | **Primary Key:** `unitid` + `cipcode` + `credential_level`

#### Program Identity
| Field | Type | Description | Use Case |
|-------|------|-------------|----------|
| `unitid` | STRING | Institution ID | Links to IPEDS |
| `cipcode` | STRING | CIP code | Program classification |
| `credential_level` | INTEGER | Credential level | Award type |
| `cip_title` | STRING | CIP title | Program name |
| `credential_title` | STRING | Credential title | Award name |

#### Credential Level Mapping
| Value | Description | CTDL Equivalent |
|-------|-------------|-----------------|
| 1 | Undergraduate Certificate | ceterms:Certificate |
| 2 | Associate's Degree | ceterms:AssociateDegree |
| 3 | Bachelor's Degree | ceterms:BachelorDegree |
| 4 | Post-baccalaureate Certificate | ceterms:Certificate |
| 5 | Master's Degree | ceterms:MasterDegree |
| 6 | Doctoral Degree | ceterms:DoctoralDegree |
| 7 | First Professional Degree | ceterms:ProfessionalDoctorate |
| 8 | Graduate Certificate | ceterms:Certificate |

#### Institution Context
| Field | Type | Description |
|-------|------|-------------|
| `school_name` | STRING | Institution name |
| `school_state` | STRING | State abbreviation |
| `school_type` | STRING | Institution type |
| `main_campus` | INTEGER | Main campus flag |
| `distance_only` | INTEGER | Distance education only |

#### Completions
| Field | Type | Description |
|-------|------|-------------|
| `ipeds_awards_yr1` | INTEGER | Awards year 1 |
| `ipeds_awards_yr2` | INTEGER | Awards year 2 |

#### Earnings Outcomes (1 Year Post-Completion)
| Field | Type | Description |
|-------|------|-------------|
| `earn_1yr_median` | FLOAT | Median earnings 1 year after |
| `earn_1yr_male_median` | FLOAT | Male median earnings |
| `earn_1yr_female_median` | FLOAT | Female median earnings |
| `earn_1yr_pell_median` | FLOAT | Pell recipient median |
| `earn_1yr_nonpell_median` | FLOAT | Non-Pell median |
| `earn_1yr_count` | INTEGER | Count in earnings sample |

#### Earnings Outcomes (4 Years Post-Completion)
| Field | Type | Description |
|-------|------|-------------|
| `earn_4yr_median` | FLOAT | Median earnings 4 years after |
| `earn_4yr_male_median` | FLOAT | Male median earnings |
| `earn_4yr_female_median` | FLOAT | Female median earnings |
| `earn_4yr_pell_median` | FLOAT | Pell recipient median |
| `earn_4yr_nonpell_median` | FLOAT | Non-Pell median |
| `earn_4yr_count` | INTEGER | Count in earnings sample |

#### Earnings Outcomes (5 Years Post-Completion)
| Field | Type | Description |
|-------|------|-------------|
| `earn_5yr_median` | FLOAT | Median earnings 5 years after |
| `earn_5yr_count` | INTEGER | Count in earnings sample |

#### Debt Data
| Field | Type | Description |
|-------|------|-------------|
| `debt_parent_plus_median` | FLOAT | Parent PLUS loan median |
| `debt_parent_plus_avg` | FLOAT | Parent PLUS loan average |
| `debt_parent_plus_count` | INTEGER | Parent PLUS count |
| `debt_grad_plus_median` | FLOAT | Graduate PLUS loan median |
| `debt_grad_plus_avg` | FLOAT | Graduate PLUS loan average |
| `debt_grad_plus_count` | INTEGER | Graduate PLUS count |
| `debt_stafford_median` | FLOAT | Stafford loan median |
| `debt_stafford_avg` | FLOAT | Stafford loan average |

#### Employment Outcomes
| Field | Type | Description |
|-------|------|-------------|
| `working_not_enrolled_1yr` | INTEGER | Working, not enrolled (1 yr) |
| `working_not_enrolled_4yr` | INTEGER | Working, not enrolled (4 yr) |
| `not_working_not_enrolled_1yr` | INTEGER | Not working, not enrolled (1 yr) |
| `count_over_poverty_line` | INTEGER | Earning over poverty line |
| `count_working_in_state` | INTEGER | Working in state of institution |

#### Loan Repayment
| Field | Type | Description |
|-------|------|-------------|
| `repayment_1yr_making_progress` | STRING | Making progress on repayment |
| `repayment_1yr_delinquent` | STRING | Delinquent on loans |
| `repayment_1yr_default` | STRING | In default on loans |

---

### 1.5 BLS Occupation Wages (`bls_occupation_wages`)

**Records:** 0 (NEEDS LOADING) | **Primary Key:** `soc_code` + `state`

#### Current Schema
| Field | Type | Description |
|-------|------|-------------|
| `soc_code` | STRING | SOC code (XX-XXXX) |
| `occupation_title` | STRING | Occupation title |
| `employment` | INTEGER | Employment count |
| `employment_per_1000` | FLOAT | Employment per 1,000 jobs |
| `wage_mean` | FLOAT | Mean annual wage |
| `wage_median` | FLOAT | Median annual wage |
| `wage_pct_10` | FLOAT | 10th percentile wage |
| `wage_pct_25` | FLOAT | 25th percentile wage |
| `wage_pct_75` | FLOAT | 75th percentile wage |
| `wage_pct_90` | FLOAT | 90th percentile wage |
| `hourly_mean` | FLOAT | Mean hourly wage |
| `hourly_median` | FLOAT | Median hourly wage |
| `area_code` | STRING | Geographic area code |
| `area_title` | STRING | Geographic area name |
| `state` | STRING | State abbreviation |
| `data_year` | INTEGER | OEWS survey year |
| `data_source` | STRING | Source identifier (OEWS) |
| `ingested_at` | TIMESTAMP | When record was loaded |

#### Data Loaded ✅
- **Source:** BLS Occupational Employment and Wage Statistics (OEWS)
- **URL:** https://www.bls.gov/oes/special-requests/oes_research_2024_allsectors.xlsx
- **Format:** Excel research estimates file
- **Records Loaded:** 34,525

---

### 1.6 CIP-SOC Crosswalk (`cip_soc_crosswalk`) ✅

**Records:** 6,097 | **Purpose:** Link credentials to occupations

#### Data Loaded ✅
- **Source:** NCES CIP-SOC Crosswalk
- **URL:** https://nces.ed.gov/ipeds/cipcode/Files/CIP2020_SOC2018_Crosswalk.xlsx
- **Records Loaded:** 6,097 mappings
- **CIP Coverage:** 2,143 unique CIP codes
- **SOC Coverage:** 868 unique SOC codes

#### Schema
| Field | Type | Description |
|-------|------|-------------|
| `cip_code` | STRING | CIP code (XX.XXXX) |
| `cip_title` | STRING | CIP title |
| `soc_code` | STRING | SOC code (XX-XXXX) |
| `soc_title` | STRING | SOC title |
| `match_type` | STRING | primary, secondary, related |
| `match_confidence` | FLOAT | Confidence 0-1 (1.0 for NCES) |
| `cip_2digit` | STRING | CIP major group |
| `soc_major` | STRING | SOC major group |
| `data_source` | STRING | Source identifier (NCES) |
| `data_year` | INTEGER | Crosswalk version year |
| `created_at` | TIMESTAMP | When record was created |

---

### 1.7 National Credentials (`national_credentials`) ✅ NEW

**Records:** 7,955 | **Primary Key:** `credential_id` (CIP + level)

This is the unified national credential table aggregating all data sources.

#### Core Identity
| Field | Type | Description |
|-------|------|-------------|
| `credential_id` | STRING | Generated ID (CIP_level format) |
| `cip_code` | STRING | CIP code (XX.XXXX) |
| `cip_title` | STRING | CIP title from crosswalk |
| `credential_level` | INTEGER | IPEDS award level (1-12) |
| `credential_name` | STRING | Human-readable credential name |

#### Classification
| Field | Type | Description |
|-------|------|-------------|
| `cip_2digit` | STRING | CIP major group (first 2 digits) |
| `cip_4digit` | STRING | CIP minor group (XX.XX) |
| `cip_family` | STRING | CIP family name (e.g., "Health Professions") |

#### National Aggregates
| Field | Type | Description |
|-------|------|-------------|
| `total_completions` | INTEGER | Total completions nationally |
| `institution_count` | INTEGER | Number of institutions offering |
| `state_count` | INTEGER | Number of states with programs |
| `top_states` | JSON | Top 10 states by completions |

#### Occupation Linkages
| Field | Type | Description |
|-------|------|-------------|
| `primary_soc_codes` | JSON | Array of linked SOC codes |
| `occupation_count` | INTEGER | Number of linked occupations |

#### Wage Outcomes (via BLS)
| Field | Type | Description |
|-------|------|-------------|
| `wage_median_national` | FLOAT | Median wage (employment-weighted) |
| `wage_mean_national` | FLOAT | Mean wage (employment-weighted) |
| `wage_pct_10` | FLOAT | 10th percentile wage |
| `wage_pct_90` | FLOAT | 90th percentile wage |
| `employment_total` | INTEGER | Total employment in linked occupations |

#### Quality Indicators
| Field | Type | Description |
|-------|------|-------------|
| `has_scorecard_data` | BOOL | Has College Scorecard outcomes |
| `has_wage_data` | BOOL | Has BLS wage data |
| `data_completeness_score` | FLOAT | 0-1 score of data availability |

#### Metadata
| Field | Type | Description |
|-------|------|-------------|
| `data_year` | INTEGER | Most recent data year |
| `ipeds_data_year` | INTEGER | IPEDS source year |
| `bls_data_year` | INTEGER | BLS source year |
| `created_at` | TIMESTAMP | When record was created |
| `updated_at` | TIMESTAMP | When record was last updated |

---

### 1.8 Completions Metadata Fields

All IPEDS completions include these metadata fields for temporal alignment:

| Field | Type | Description |
|-------|------|-------------|
| `data_year` | INTEGER | IPEDS survey year (e.g., 2022 for 2022-23 academic year) |
| `ingested_at` | TIMESTAMP | When the record was loaded into BigQuery |

---

### 1.8 Scorecard Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `data_year` | INTEGER | Scorecard data year |
| `ingested_at` | TIMESTAMP | When the record was loaded into BigQuery |

---

### 1.9 Cross-Source Linkage Schema

This section documents how all data sources connect to form the unified national credential database.

#### Primary Link: UNITID (Institution Level)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           UNITID LINKAGES                               │
│                    (Primary Institutional Identifier)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────┐          ┌─────────────────────┐             │
│   │ ipeds_institutions  │◄─────────┤ ipeds_completions   │             │
│   │ (6,163 institutions)│  unitid  │ (303,292 programs)  │             │
│   └─────────┬───────────┘          └──────────┬──────────┘             │
│             │                                  │                        │
│             │ unitid                           │ unitid + cipcode       │
│             ▼                                  │ + credential_level     │
│   ┌─────────────────────┐                     ▼                        │
│   │ipeds_characteristics│          ┌─────────────────────┐             │
│   │ (6,049 records)     │          │ scorecard_programs  │             │
│   └─────────────────────┘          │ (213,711 programs)  │             │
│                                    └─────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Secondary Link: CIP Code (Program Level)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CIP CODE LINKAGES                              │
│           (Classification of Instructional Programs - XX.XXXX)          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────┐     cipcode     ┌─────────────────────┐      │
│   │ ipeds_completions   │◄───────────────►│ scorecard_programs  │      │
│   │ (303,292 records)   │                 │ (213,711 records)   │      │
│   └──────────┬──────────┘                 └──────────┬──────────┘      │
│              │                                       │                  │
│              │ cipcode                               │ cipcode          │
│              ▼                                       ▼                  │
│   ┌───────────────────────────────────────────────────────────┐        │
│   │                      cip_codes                             │        │
│   │            (Reference table with CIP titles)               │        │
│   └─────────────────────────┬─────────────────────────────────┘        │
│                             │                                           │
│                             │ cip_code                                  │
│                             ▼                                           │
│   ┌───────────────────────────────────────────────────────────┐        │
│   │                   cip_soc_crosswalk                        │        │
│   │        (Maps CIP codes to SOC occupation codes)            │        │
│   └─────────────────────────┬─────────────────────────────────┘        │
│                             │                                           │
│                             │ soc_code                                  │
│                             ▼                                           │
│   ┌───────────────────────────────────────────────────────────┐        │
│   │                  bls_occupation_wages                      │        │
│   │            (Wage data by SOC code and state)               │        │
│   └───────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Link Field Specifications

| Source Table | Target Table | Link Field(s) | Cardinality | Notes |
|--------------|--------------|---------------|-------------|-------|
| `ipeds_completions` | `ipeds_institutions` | `unitid` | Many-to-One | Every completion links to one institution |
| `ipeds_characteristics` | `ipeds_institutions` | `unitid` | One-to-One | Characteristics are per institution |
| `scorecard_programs` | `ipeds_institutions` | `unitid` | Many-to-One | Scorecard uses same UNITID |
| `ipeds_completions` | `scorecard_programs` | `unitid` + `cipcode` + `awlevel`/`credential_level` | One-to-One* | Award level mapping required |
| `ipeds_completions` | `cip_codes` | `cipcode` | Many-to-One | CIP lookup for titles |
| `cip_soc_crosswalk` | `bls_occupation_wages` | `soc_code` + `state` | Many-to-One | State-specific wages |

*Note: Award level mapping between IPEDS `awlevel` (1-12) and Scorecard `credential_level` (1-8) requires translation.

#### Award Level Translation Matrix

| IPEDS `awlevel` | IPEDS Description | Scorecard `credential_level` | Scorecard Description |
|-----------------|-------------------|------------------------------|----------------------|
| 1 | Award < 1 year | 1 | Undergraduate Certificate |
| 2 | Award 1-2 years | 1 | Undergraduate Certificate |
| 3 | Associate's | 2 | Associate's Degree |
| 4 | Award 2-4 years | 1 | Undergraduate Certificate |
| 5 | Bachelor's | 3 | Bachelor's Degree |
| 6 | Post-bacc cert | 4 | Post-baccalaureate Certificate |
| 7 | Master's | 5 | Master's Degree |
| 8 | Post-master's cert | 8 | Graduate Certificate |
| 9 | Doctorate - Research | 6 | Doctoral Degree |
| 10 | Doctorate - Professional | 7 | First Professional Degree |
| 11 | Doctorate - Other | 6 | Doctoral Degree |
| 12 | Other award | 1 | Undergraduate Certificate |

#### Geographic Linkage

| Level | IPEDS Field | BLS Field | Join Logic |
|-------|-------------|-----------|------------|
| State | `stabbr` | `state` | Exact match (2-letter code) |
| Metro | `cbsa` | `area_code` | Exact match (5-digit CBSA) |
| National | N/A | `area_code = '000000'` | National totals |

#### Complete Join Path: Credential to Wages

```sql
-- Full credential-to-wage linkage path
SELECT
  -- Credential identity
  c.unitid,
  c.cipcode,
  c.awlevel,

  -- Institution context
  i.instnm as institution_name,
  i.stabbr as state,
  i.control,
  i.iclevel,

  -- Program completions
  c.ctotalt as completions,

  -- Scorecard earnings (credential-specific)
  sc.earn_1yr_median,
  sc.earn_4yr_median,

  -- BLS wages (occupation-wide)
  bls.wage_median as occupation_median_wage,
  bls.employment as occupation_employment

FROM `credential-bridge.credential_bridge.ipeds_completions` c

-- Institution enrichment
JOIN `credential-bridge.credential_bridge.ipeds_institutions` i
  ON c.unitid = i.unitid

-- Scorecard outcomes (where available)
LEFT JOIN `credential-bridge.credential_bridge.scorecard_programs` sc
  ON c.unitid = sc.unitid
  AND c.cipcode = sc.cipcode
  AND CASE c.awlevel
        WHEN 1 THEN 1 WHEN 2 THEN 1 WHEN 3 THEN 2 WHEN 4 THEN 1
        WHEN 5 THEN 3 WHEN 6 THEN 4 WHEN 7 THEN 5 WHEN 8 THEN 8
        WHEN 9 THEN 6 WHEN 10 THEN 7 WHEN 11 THEN 6 WHEN 12 THEN 1
      END = sc.credential_level

-- CIP to SOC mapping
LEFT JOIN `credential-bridge.credential_bridge.cip_soc_crosswalk` xw
  ON c.cipcode = xw.cip_code

-- BLS wages by occupation and state
LEFT JOIN `credential-bridge.credential_bridge.bls_occupation_wages` bls
  ON xw.soc_code = bls.soc_code
  AND i.stabbr = bls.state

WHERE i.cyactive = 1  -- Active institutions only
  AND c.ctotalt > 0   -- Has completions
```

---

## Part 2: Implementation Plan

### Phase 2A: Data Loading & Validation ✅ COMPLETE

#### Step 2A.1: Load BLS Occupation Wage Data ✅

**Status:** ✅ Complete (December 15, 2025)
**Script:** `scripts/load_bls_wages.py`

**Results:**
| Metric | Value |
|--------|-------|
| Records Loaded | 34,525 |
| Unique SOC Codes | 831 |
| States/Territories | 52 |
| Data Year | 2024 |

**Implementation Notes:**
- BLS OEWS data is NOT available via Public Data API
- Downloaded Excel research estimates from https://www.bls.gov/oes/special-requests/
- Enterprise-grade loader with retry logic, validation, audit trail
- Employment-weighted national averages computed from state data

#### Step 2A.2: Expand CIP-SOC Crosswalk ✅

**Status:** ✅ Complete (December 15, 2025)
**Script:** `scripts/load_cip_soc_crosswalk.py`

**Results:**
| Metric | Value |
|--------|-------|
| Mappings Loaded | 6,097 |
| Unique CIP Codes | 2,143 |
| Unique SOC Codes | 868 |
| Data Source | NCES CIP2020/SOC2018 |

**Implementation Notes:**
- Downloaded official NCES crosswalk from https://nces.ed.gov/ipeds/cipcode/Files/CIP2020_SOC2018_Crosswalk.xlsx
- Reads from "CIP-SOC" sheet (multiple sheets in file)
- Enterprise-grade loader with validation, retry logic, audit trail
- All mappings marked as primary with 1.0 confidence (authoritative source)

---

### Phase 2B: National Credential Generation ✅ COMPLETE

#### Step 2B.1: Generate National Credentials Table ✅

**Status:** ✅ Complete (December 15, 2025)
**Script:** `scripts/generate_national_credentials.py`

**Results:**
| Metric | Value |
|--------|-------|
| Credentials Generated | 7,955 |
| Unique CIP Codes | 1,560 |
| Credential Levels | 12 |
| Total Completions | 10,795,332 |
| With Wage Data | 7,420 (93%) |
| With Scorecard Data | 3,465 (44%) |
| Avg Completeness | 92.4% |

**Implementation Notes:**
- Aggregates IPEDS completions by CIP code + credential level
- Links to CIP-SOC crosswalk for occupation mappings
- Computes employment-weighted national wage averages from state BLS data
- Includes top 10 states by completions (JSON array)
- Data completeness score based on IPEDS, wages, occupations, state coverage

#### Step 2B.2: Create Unified Credential View (Legacy)

Create a view that combines IPEDS completions with institution data:

```sql
CREATE OR REPLACE VIEW `credential-bridge.credential_bridge.v_ipeds_credentials` AS
SELECT
  -- Credential Identity
  CONCAT('ipeds-', c.unitid, '-', c.cipcode, '-', CAST(c.awlevel AS STRING)) as credential_id,

  -- Program Info
  c.cipcode,
  c.awlevel,
  c.majornum,

  -- Institution Info
  i.unitid,
  i.instnm as institution_name,
  i.opeid,
  i.stabbr as state,
  i.city,
  i.zip,
  i.latitude,
  i.longitude,

  -- Institution Classification
  i.sector,
  i.iclevel,
  i.control,
  i.hloffer,
  i.instsize,
  i.hbcu,
  i.tribal,
  i.landgrnt,

  -- Carnegie
  i.c21basic as carnegie_basic,

  -- System
  i.f1sysnam as system_name,

  -- Completions
  c.ctotalt as total_completions,
  c.ctotalm as male_completions,
  c.ctotalw as female_completions,

  -- Race/Ethnicity Completions
  c.caiant as aian_completions,
  c.casiat as asian_completions,
  c.cbkaat as black_completions,
  c.chispt as hispanic_completions,
  c.cnhpit as nhpi_completions,
  c.cwhitt as white_completions,
  c.c2mort as multiracial_completions,
  c.cunknt as unknown_race_completions,
  c.cnralt as nonresident_completions,

  -- Metadata
  c.data_year,
  CURRENT_TIMESTAMP() as generated_at

FROM `credential-bridge.credential_bridge.ipeds_completions` c
JOIN `credential-bridge.credential_bridge.ipeds_institutions` i
  ON c.unitid = i.unitid
WHERE i.cyactive = 1  -- Active institutions only
  AND c.ctotalt > 0   -- Has completions
```

#### Step 2B.2: Create Award Level Reference

```sql
CREATE OR REPLACE TABLE `credential-bridge.credential_bridge.ref_award_levels` AS
SELECT * FROM UNNEST([
  STRUCT(1 as awlevel, 'Award of less than 1 academic year' as description,
         'Certificate' as ctdl_type, 'ceterms:Certificate' as ctdl_uri),
  STRUCT(2, 'Award of at least 1 but less than 2 academic years',
         'Certificate', 'ceterms:Certificate'),
  STRUCT(3, 'Associate''s degree',
         'AssociateDegree', 'ceterms:AssociateDegree'),
  STRUCT(4, 'Award of at least 2 but less than 4 academic years',
         'Certificate', 'ceterms:Certificate'),
  STRUCT(5, 'Bachelor''s degree',
         'BachelorDegree', 'ceterms:BachelorDegree'),
  STRUCT(6, 'Postbaccalaureate certificate',
         'Certificate', 'ceterms:Certificate'),
  STRUCT(7, 'Master''s degree',
         'MasterDegree', 'ceterms:MasterDegree'),
  STRUCT(8, 'Post-master''s certificate',
         'Certificate', 'ceterms:Certificate'),
  STRUCT(9, 'Doctor''s degree - research/scholarship',
         'ResearchDoctorate', 'ceterms:ResearchDoctorate'),
  STRUCT(10, 'Doctor''s degree - professional practice',
         'ProfessionalDoctorate', 'ceterms:ProfessionalDoctorate'),
  STRUCT(11, 'Doctor''s degree - other',
         'DoctoralDegree', 'ceterms:DoctoralDegree'),
  STRUCT(12, 'Other award',
         'Certificate', 'ceterms:Certificate')
])
```

#### Step 2B.3: Generate National Credentials Table

```sql
CREATE OR REPLACE TABLE `credential-bridge.credential_bridge.national_credentials` AS
SELECT
  -- CTID (Credential Transparency ID)
  CONCAT('ipeds-', v.unitid, '-', v.cipcode, '-', CAST(v.awlevel AS STRING)) as ctid,

  -- Names
  CONCAT(r.description, ' in ', COALESCE(cip.cip_title, v.cipcode)) as name,
  CONCAT(v.institution_name, ' - ', COALESCE(cip.cip_title, v.cipcode)) as full_name,

  -- CTDL Type
  r.ctdl_type as credential_type,
  r.ctdl_uri as credential_type_uri,

  -- CIP Classification
  v.cipcode as cip_code,
  LEFT(v.cipcode, 2) as cip_2digit,
  cip.cip_title,
  cip.cip_definition,

  -- Award Level
  v.awlevel as award_level,
  r.description as award_level_description,

  -- Provider Institution
  v.unitid,
  v.institution_name,
  v.opeid,
  v.state,
  v.city,
  v.zip,
  v.latitude,
  v.longitude,

  -- Institution Classification
  CASE v.control
    WHEN 1 THEN 'public'
    WHEN 2 THEN 'private_nonprofit'
    WHEN 3 THEN 'private_for_profit'
  END as institution_control,

  CASE v.iclevel
    WHEN 1 THEN '4-year'
    WHEN 2 THEN '2-year'
    WHEN 3 THEN 'less-than-2-year'
  END as institution_level,

  v.carnegie_basic,
  v.system_name,
  v.hbcu,
  v.tribal,
  v.landgrnt as land_grant,

  -- Completion Statistics
  v.total_completions,
  v.male_completions,
  v.female_completions,

  -- Demographics
  STRUCT(
    v.aian_completions as american_indian_alaska_native,
    v.asian_completions as asian,
    v.black_completions as black_african_american,
    v.hispanic_completions as hispanic_latino,
    v.nhpi_completions as native_hawaiian_pacific_islander,
    v.white_completions as white,
    v.multiracial_completions as two_or_more_races,
    v.unknown_race_completions as unknown,
    v.nonresident_completions as nonresident_alien
  ) as completions_by_race,

  -- Source Tracking
  'ipeds' as source_type,
  v.data_year as source_year,
  CURRENT_TIMESTAMP() as ingested_at

FROM `credential-bridge.credential_bridge.v_ipeds_credentials` v
LEFT JOIN `credential-bridge.credential_bridge.ref_award_levels` r
  ON v.awlevel = r.awlevel
LEFT JOIN `credential-bridge.credential_bridge.cip_codes` cip
  ON v.cipcode = cip.cip_code
```

---

### Phase 3A: College Scorecard Enrichment ✅ COMPLETE

**Status:** ✅ Complete (December 15, 2025)
**View Created:** `v_national_credentials_scorecard`
**Records Linked:** 3,465 credentials with Scorecard earnings data (44%)

#### Actual Implementation

The College Scorecard linkage was implemented with:
- CIP code format translation (4-digit to XX.XX)
- Credential level matching
- Aggregate 1-year and 4-year median earnings

```sql
-- View created: v_national_credentials_scorecard
-- Links national_credentials to scorecard_programs via CIP + credential_level
```

#### Step 3A.1: Link Scorecard to National Credentials (Original Plan)

```sql
-- Original plan - now superseded by v_national_credentials_scorecard
CREATE OR REPLACE VIEW `credential-bridge.credential_bridge.v_credentials_with_outcomes` AS
SELECT
  nc.*,

  -- 1-Year Earnings
  sc.earn_1yr_median,
  sc.earn_1yr_male_median,
  sc.earn_1yr_female_median,
  sc.earn_1yr_pell_median,
  sc.earn_1yr_nonpell_median,
  sc.earn_1yr_count,

  -- 4-Year Earnings
  sc.earn_4yr_median,
  sc.earn_4yr_male_median,
  sc.earn_4yr_female_median,
  sc.earn_4yr_pell_median,
  sc.earn_4yr_nonpell_median,
  sc.earn_4yr_count,

  -- 5-Year Earnings
  sc.earn_5yr_median,
  sc.earn_5yr_count,

  -- Debt
  sc.debt_stafford_median,
  sc.debt_stafford_avg,
  sc.debt_parent_plus_median,
  sc.debt_grad_plus_median,

  -- Employment
  sc.working_not_enrolled_1yr,
  sc.working_not_enrolled_4yr,
  sc.count_over_poverty_line,
  sc.count_working_in_state,

  -- Loan Repayment
  sc.repayment_1yr_making_progress,
  sc.repayment_1yr_delinquent,
  sc.repayment_1yr_default,

  -- Scorecard metadata
  sc.distance_only as scorecard_distance_only,
  CASE WHEN sc.unitid IS NOT NULL THEN TRUE ELSE FALSE END as has_scorecard_data

FROM `credential-bridge.credential_bridge.national_credentials` nc
LEFT JOIN `credential-bridge.credential_bridge.scorecard_programs` sc
  ON nc.unitid = sc.unitid
  AND nc.cip_code = sc.cipcode
  AND nc.award_level = sc.credential_level
```

#### Step 3A.2: Create Scorecard-Only Programs

Some programs exist in Scorecard but not in IPEDS completions:

```sql
-- Insert programs from Scorecard not in IPEDS
INSERT INTO `credential-bridge.credential_bridge.national_credentials`
SELECT
  CONCAT('scorecard-', sc.unitid, '-', sc.cipcode, '-', CAST(sc.credential_level AS STRING)) as ctid,
  sc.credential_title as name,
  CONCAT(sc.school_name, ' - ', sc.cip_title) as full_name,
  r.ctdl_type as credential_type,
  r.ctdl_uri as credential_type_uri,
  sc.cipcode as cip_code,
  LEFT(sc.cipcode, 2) as cip_2digit,
  sc.cip_title,
  NULL as cip_definition,
  sc.credential_level as award_level,
  sc.credential_title as award_level_description,
  sc.unitid,
  sc.school_name as institution_name,
  NULL as opeid,
  sc.school_state as state,
  -- ... fill remaining fields from institution join
  'scorecard' as source_type,
  sc.data_year as source_year,
  CURRENT_TIMESTAMP() as ingested_at
FROM `credential-bridge.credential_bridge.scorecard_programs` sc
LEFT JOIN `credential-bridge.credential_bridge.national_credentials` nc
  ON sc.unitid = nc.unitid
  AND sc.cipcode = nc.cip_code
  AND sc.credential_level = nc.award_level
WHERE nc.ctid IS NULL  -- Not already in national_credentials
```

---

### Phase 3B: BLS Wage Integration ✅ COMPLETE

**Status:** ✅ Complete (December 15, 2025)
**Records Linked:** 7,420 credentials with wage data (93%)
**View Created:** `v_credential_occupations`

#### Actual Implementation

The BLS wage linkage was implemented directly in the `national_credentials` table:
- Employment-weighted national wage averages computed from state-level BLS data
- Linked via CIP-SOC crosswalk (6,097 mappings)
- Wage columns: `wage_median_national`, `wage_mean_national`, `wage_pct_10`, `wage_pct_90`
- `has_wage_data` flag set for 93% of credentials

```sql
-- Wage data integrated into national_credentials table
-- via CIP → SOC crosswalk → BLS OEWS state wages (aggregated to national)
```

#### Step 3B.1: Link Credentials to Occupations via CIP-SOC (Original Plan)

```sql
CREATE OR REPLACE VIEW `credential-bridge.credential_bridge.v_credentials_occupations` AS
SELECT
  nc.ctid,
  nc.name,
  nc.cip_code,
  nc.state,

  -- Occupation Links
  xw.soc_code,
  xw.soc_title,
  xw.match_type,
  xw.match_confidence,

  -- State-Specific Wage Data
  bls.employment as occupation_employment,
  bls.wage_median as occupation_wage_median,
  bls.wage_mean as occupation_wage_mean,
  bls.wage_pct_10 as occupation_wage_p10,
  bls.wage_pct_25 as occupation_wage_p25,
  bls.wage_pct_75 as occupation_wage_p75,
  bls.wage_pct_90 as occupation_wage_p90,

  -- National Wage Data (for comparison)
  bls_nat.wage_median as national_wage_median,
  bls_nat.employment as national_employment

FROM `credential-bridge.credential_bridge.national_credentials` nc
JOIN `credential-bridge.credential_bridge.cip_soc_crosswalk` xw
  ON nc.cip_code = xw.cip_code
LEFT JOIN `credential-bridge.credential_bridge.bls_occupation_wages` bls
  ON xw.soc_code = bls.soc_code
  AND nc.state = bls.state
LEFT JOIN `credential-bridge.credential_bridge.bls_occupation_wages` bls_nat
  ON xw.soc_code = bls_nat.soc_code
  AND bls_nat.area_code = '000000'  -- National
```

#### Step 3B.2: Create Aggregate Credential-Occupation View

```sql
CREATE OR REPLACE VIEW `credential-bridge.credential_bridge.v_credential_outcomes` AS
SELECT
  nc.ctid,
  nc.name,
  nc.credential_type,
  nc.cip_code,
  nc.institution_name,
  nc.state,
  nc.total_completions,

  -- Scorecard Earnings
  sc.earn_1yr_median as earnings_1yr,
  sc.earn_4yr_median as earnings_4yr,
  sc.debt_stafford_median as debt_median,

  -- Best Occupation Match
  ARRAY_AGG(
    STRUCT(
      co.soc_code,
      co.soc_title,
      co.occupation_wage_median,
      co.occupation_employment,
      co.match_confidence
    )
    ORDER BY co.match_confidence DESC, co.occupation_employment DESC
    LIMIT 5
  ) as top_occupations,

  -- Aggregate Occupation Stats
  AVG(co.occupation_wage_median) as avg_occupation_wage,
  SUM(co.occupation_employment) as total_occupation_employment,
  COUNT(DISTINCT co.soc_code) as linked_occupation_count

FROM `credential-bridge.credential_bridge.national_credentials` nc
LEFT JOIN `credential-bridge.credential_bridge.v_credentials_with_outcomes` sc
  ON nc.ctid = sc.ctid
LEFT JOIN `credential-bridge.credential_bridge.v_credentials_occupations` co
  ON nc.ctid = co.ctid
GROUP BY 1,2,3,4,5,6,7,8,9,10
```

---

## Part 3: Materialized Tables for Performance

### Final National Credentials Table Schema

```sql
CREATE TABLE `credential-bridge.credential_bridge.national_credentials_enriched` (
  -- Identity
  ctid STRING NOT NULL,
  name STRING NOT NULL,
  full_name STRING,

  -- CTDL Classification
  credential_type STRING,
  credential_type_uri STRING,
  credential_status STRING DEFAULT 'Active',

  -- CIP Classification
  cip_code STRING NOT NULL,
  cip_2digit STRING,
  cip_title STRING,
  cip_definition STRING,

  -- Award Level
  award_level INT64,
  award_level_description STRING,

  -- Provider
  unitid STRING NOT NULL,
  institution_name STRING NOT NULL,
  opeid STRING,
  institution_control STRING,
  institution_level STRING,
  carnegie_basic INT64,
  system_name STRING,
  hbcu BOOL,
  tribal BOOL,
  land_grant BOOL,

  -- Location
  state STRING NOT NULL,
  city STRING,
  zip STRING,
  latitude FLOAT64,
  longitude FLOAT64,

  -- Completions
  total_completions INT64,
  male_completions INT64,
  female_completions INT64,
  completions_by_race STRUCT<
    american_indian_alaska_native INT64,
    asian INT64,
    black_african_american INT64,
    hispanic_latino INT64,
    native_hawaiian_pacific_islander INT64,
    white INT64,
    two_or_more_races INT64,
    unknown INT64,
    nonresident_alien INT64
  >,

  -- Scorecard Outcomes
  has_scorecard_data BOOL,
  earnings_1yr_median FLOAT64,
  earnings_4yr_median FLOAT64,
  earnings_5yr_median FLOAT64,
  debt_median FLOAT64,
  working_rate_1yr FLOAT64,
  working_rate_4yr FLOAT64,

  -- BLS Occupation Links
  primary_soc_code STRING,
  primary_soc_title STRING,
  primary_occupation_wage_median FLOAT64,
  primary_occupation_employment INT64,
  linked_occupation_count INT64,

  -- Source Tracking
  source_type STRING,
  source_year INT64,

  -- Metadata
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(ingested_at)
CLUSTER BY state, credential_type, cip_2digit
```

---

## Part 4: Implementation Scripts

### Script 1: Load BLS Data

**File:** `scripts/load_bls_wages.py`

```python
"""Load BLS OEWS data for all states."""

import asyncio
import pandas as pd
from pathlib import Path

async def load_bls_state_data():
    """Download and load BLS wage data for all states."""

    # BLS OEWS state file URL pattern
    base_url = "https://www.bls.gov/oes/special.requests/"

    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'GU', 'VI'
    ]

    all_records = []

    for state in states:
        # Load state data
        # Parse and normalize
        # Append to records
        pass

    # Upload to BigQuery
    return len(all_records)
```

### Script 2: Load CIP-SOC Crosswalk

**File:** `scripts/load_cip_soc_crosswalk.py`

```python
"""Load complete CIP-SOC crosswalk from NCES."""

import asyncio
import pandas as pd

async def load_crosswalk():
    """Download and load CIP-SOC crosswalk."""

    # NCES crosswalk URL
    url = "https://nces.ed.gov/ipeds/cipcode/Files/CIP2020_SOC2018_Crosswalk.xlsx"

    # Download and parse
    df = pd.read_excel(url)

    # Normalize fields
    # Calculate match confidence
    # Upload to BigQuery

    return len(df)
```

### Script 3: Generate National Credentials

**File:** `scripts/generate_national_credentials.py`

```python
"""Generate national credentials table from all sources."""

import asyncio
from credential_bridge.services.bigquery_service import get_bigquery_service

async def generate_national_credentials():
    """Execute all SQL steps to generate national credentials."""

    bq = get_bigquery_service()

    steps = [
        ("Create IPEDS view", "sql/create_ipeds_view.sql"),
        ("Create award levels", "sql/create_award_levels.sql"),
        ("Generate national credentials", "sql/generate_national_credentials.sql"),
        ("Link Scorecard outcomes", "sql/link_scorecard.sql"),
        ("Link BLS wages", "sql/link_bls_wages.sql"),
        ("Create enriched table", "sql/create_enriched_table.sql"),
    ]

    for name, sql_file in steps:
        print(f"Executing: {name}")
        sql = Path(sql_file).read_text()
        await bq.execute_query(sql, operation=name)

    return True
```

---

## Part 5: Validation Checklist

### Data Quality Checks

- [ ] All 50 states + territories have IPEDS institutions
- [ ] All active institutions have at least one completion record
- [ ] All CIP codes in completions have valid 6-digit format
- [ ] BLS data covers all major SOC codes (800+)
- [ ] CIP-SOC crosswalk covers 90%+ of completion CIP codes
- [ ] Scorecard linkage rate > 60% of IPEDS programs
- [ ] No duplicate CTIDs in national_credentials
- [ ] All credential_type values are valid CTDL types

### Coverage Validation

```sql
-- Check state coverage
SELECT state, COUNT(*) as credentials
FROM national_credentials
GROUP BY state
ORDER BY credentials DESC;

-- Check CIP coverage
SELECT cip_2digit, COUNT(*) as credentials
FROM national_credentials
GROUP BY cip_2digit
ORDER BY credentials DESC;

-- Check Scorecard linkage rate
SELECT
  COUNT(*) as total,
  COUNTIF(has_scorecard_data) as with_scorecard,
  COUNTIF(has_scorecard_data) / COUNT(*) as linkage_rate
FROM national_credentials;

-- Check BLS linkage rate
SELECT
  COUNT(*) as total,
  COUNTIF(linked_occupation_count > 0) as with_bls,
  COUNTIF(linked_occupation_count > 0) / COUNT(*) as linkage_rate
FROM national_credentials_enriched;
```

---

## Part 6: Timeline and Dependencies

### Execution Order

```
Phase 2A: Data Loading (Day 1-2)
├── 2A.1: Load BLS Wages
├── 2A.2: Expand CIP-SOC Crosswalk
└── 2A.3: Validate data quality

Phase 2B: National Credentials (Day 3-4)
├── 2B.1: Create IPEDS credential view
├── 2B.2: Create reference tables
├── 2B.3: Generate national_credentials table
└── 2B.4: Validate coverage

Phase 3A: Scorecard Enrichment (Day 5)
├── 3A.1: Link Scorecard outcomes
├── 3A.2: Insert Scorecard-only programs
└── 3A.3: Validate earnings coverage

Phase 3B: BLS Integration (Day 6)
├── 3B.1: Create occupation linkages
├── 3B.2: Create aggregate views
└── 3B.3: Validate wage coverage

Phase 3C: Final Assembly (Day 7-8)
├── 3C.1: Create enriched table
├── 3C.2: Run all validation queries
├── 3C.3: Create API views
└── 3C.4: Update state assessments
```

### Dependencies

```
BLS Wages ──────────────────┐
                            ├──► Occupation Linkages ──► Enriched Table
CIP-SOC Crosswalk ──────────┘

IPEDS Institutions ─────────┐
                            ├──► National Credentials ──┬──► Enriched Table
IPEDS Completions ──────────┘                          │
                                                       │
College Scorecard ─────────────────────────────────────┘
```

---

## Appendix A: CIP Code Reference

### 2-Digit CIP Major Groups

| Code | Title | Example Programs |
|------|-------|------------------|
| 01 | Agriculture | Agricultural Business, Animal Sciences |
| 03 | Natural Resources | Environmental Science, Forestry |
| 04 | Architecture | Architecture, Urban Planning |
| 05 | Area Studies | African Studies, Asian Studies |
| 09 | Communication | Journalism, Public Relations |
| 10 | Communications Technologies | Graphic Communications |
| 11 | Computer Science | Computer Programming, IT |
| 12 | Personal Services | Cosmetology, Culinary Arts |
| 13 | Education | Elementary Education, Special Education |
| 14 | Engineering | Civil, Electrical, Mechanical |
| 15 | Engineering Technologies | CAD, Electronics |
| 16 | Foreign Languages | Spanish, French, Chinese |
| 19 | Family Sciences | Human Development, Nutrition |
| 22 | Legal Studies | Paralegal, Legal Assistant |
| 23 | English | Literature, Creative Writing |
| 24 | Liberal Arts | General Studies, Humanities |
| 25 | Library Science | Library Administration |
| 26 | Biological Sciences | Biology, Biochemistry |
| 27 | Mathematics | Mathematics, Statistics |
| 29 | Military Technologies | Military Science |
| 30 | Interdisciplinary | Neuroscience, Sustainability |
| 31 | Parks & Recreation | Sports Management, Tourism |
| 38 | Philosophy | Philosophy, Ethics |
| 39 | Theology | Ministry, Religious Studies |
| 40 | Physical Sciences | Chemistry, Physics |
| 41 | Science Technologies | Lab Technology |
| 42 | Psychology | Clinical, Counseling |
| 43 | Security | Criminal Justice, Fire Science |
| 44 | Public Administration | Public Policy, Social Work |
| 45 | Social Sciences | Economics, Political Science |
| 46 | Construction | Carpentry, Electrical |
| 47 | Mechanic Technologies | Auto Repair, HVAC |
| 48 | Precision Production | Machining, Welding |
| 49 | Transportation | Aviation, Trucking |
| 50 | Visual Arts | Art, Music, Theater |
| 51 | Health | Nursing, Medical Assisting |
| 52 | Business | Accounting, Marketing, Management |
| 54 | History | History, Archaeology |

---

## Appendix B: SOC Major Groups

| Code | Title | Example Occupations |
|------|-------|---------------------|
| 11 | Management | CEOs, Operations Managers |
| 13 | Business Operations | Financial Analysts, HR Specialists |
| 15 | Computer & Mathematical | Software Developers, Data Scientists |
| 17 | Architecture & Engineering | Civil Engineers, Architects |
| 19 | Life, Physical, Social Science | Biologists, Chemists |
| 21 | Community & Social Service | Social Workers, Counselors |
| 23 | Legal | Lawyers, Paralegals |
| 25 | Educational | Teachers, Professors |
| 27 | Arts & Entertainment | Graphic Designers, Musicians |
| 29 | Healthcare Practitioners | Nurses, Physicians |
| 31 | Healthcare Support | Medical Assistants, CNAs |
| 33 | Protective Service | Police, Firefighters |
| 35 | Food Preparation | Chefs, Servers |
| 37 | Building Maintenance | Janitors, Landscapers |
| 39 | Personal Care | Childcare, Fitness Trainers |
| 41 | Sales | Retail Sales, Insurance Agents |
| 43 | Office Administrative | Secretaries, Clerks |
| 45 | Farming & Fishing | Farmers, Fishers |
| 47 | Construction | Carpenters, Electricians |
| 49 | Installation & Repair | Auto Mechanics, HVAC |
| 51 | Production | Assemblers, Machinists |
| 53 | Transportation | Truck Drivers, Pilots |

---

## Appendix C: Credential Engine Integration (Phase 4 - Pending API Key)

When the Credential Engine API key is available, this section documents the integration approach.

### CE Registry API Overview

| Endpoint | Purpose | Rate Limit |
|----------|---------|------------|
| `/search` | Search credentials with filters | 100 req/min |
| `/credential/{ctid}` | Get single credential by CTID | 100 req/min |
| `/organization/{ctid}` | Get organization details | 100 req/min |

### CTDL Properties to Extract

#### Core Credential Properties

| CTDL Property | Type | Maps To |
|---------------|------|---------|
| `ceterms:ctid` | STRING | Primary identifier (ce-xxxxx format) |
| `ceterms:name` | STRING | Credential name |
| `ceterms:description` | STRING | Full description |
| `ceterms:credentialType` | URI | ceterms:Certificate, ceterms:AssociateDegree, etc. |
| `ceterms:credentialStatusType` | URI | Active, Deprecated, Suspended |
| `ceterms:subjectWebpage` | URL | Credential page |
| `ceterms:dateEffective` | DATE | When credential became effective |

#### Classification Properties

| CTDL Property | Type | Maps To |
|---------------|------|---------|
| `ceterms:subject` | STRING[] | Subject area keywords |
| `ceterms:naics` | STRING[] | NAICS industry codes |
| `ceterms:onet:soc` | STRING[] | O*NET SOC codes |
| `ceterms:instructionalProgramType` | URI[] | CIP codes (via CredentialAlignment) |

#### Provider Properties

| CTDL Property | Type | Maps To |
|---------------|------|---------|
| `ceterms:offeredBy` | URI[] | Organization CTIDs |
| `ceterms:ownedBy` | URI[] | Owning organization |
| `ceterms:recognizedBy` | URI[] | Recognizing bodies |
| `ceterms:accreditedBy` | URI[] | Accrediting agencies |

#### Requirements

| CTDL Property | Type | Maps To |
|---------------|------|---------|
| `ceterms:requires` | ConditionProfile[] | Entry requirements |
| `ceterms:corequisite` | ConditionProfile[] | Corequisites |
| `ceterms:recommends` | ConditionProfile[] | Recommendations |
| `ceterms:estimatedDuration` | DurationProfile | Time to complete |
| `ceterms:estimatedCost` | CostProfile[] | Cost information |

#### Outcomes & Connections

| CTDL Property | Type | Maps To |
|---------------|------|---------|
| `ceterms:isPreparationFor` | URI[] | What this prepares for |
| `ceterms:preparationFrom` | URI[] | What prepares for this |
| `ceterms:advancedStandingFrom` | URI[] | Prior credentials |
| `ceterms:isAdvancedStandingFor` | URI[] | Following credentials |

### CE to IPEDS Linkage

Credential Engine credentials link to our data via:

1. **UNITID** - Some CE organizations include IPEDS UNITID
2. **CIP Code** - Via `ceterms:instructionalProgramType` alignments
3. **SOC Code** - Via `ceterms:onet:soc` occupation codes
4. **OPEID** - Some CE organizations include DOE OPEID

```sql
-- Linking CE credentials to enriched national data
SELECT
  ce.ctid as ce_ctid,
  ce.name as ce_name,
  ce.credential_type,

  -- Match to national credentials by institution + CIP
  nc.ctid as ipeds_ctid,
  nc.total_completions,
  nc.earnings_1yr_median,
  nc.primary_occupation_wage_median

FROM `credential-bridge.credential_bridge.ce_credentials` ce
LEFT JOIN `credential-bridge.credential_bridge.national_credentials_enriched` nc
  ON ce.organization_unitid = nc.unitid
  AND ce.cip_code = nc.cip_code
  AND ce.ctdl_credential_type = nc.credential_type_uri
```

### CE Ingestion Script

**File:** `scripts/ingest_credential_engine.py`

```python
"""Ingest credentials from Credential Engine Registry."""

import asyncio
from credential_bridge.services.credential_engine import get_credential_engine_client

async def ingest_state_credentials(state_code: str):
    """Ingest all credentials for a state from CE Registry."""

    async with get_credential_engine_client() as ce_client:
        credentials = []

        async for cred in ce_client.stream_search(
            filters={"state": state_code},
            max_results=50000
        ):
            credentials.append(normalize_to_ctdl(cred))

        # Upload to BigQuery
        await upload_to_bigquery(credentials, table="ce_credentials")

        return len(credentials)
```

---

## Appendix D: CTDL Credential Type Reference

Complete list of CTDL credential types for data normalization:

| CTDL Type | URI | Description |
|-----------|-----|-------------|
| `ApprenticeshipCertificate` | `ceterms:ApprenticeshipCertificate` | Apprenticeship completion |
| `AssociateDegree` | `ceterms:AssociateDegree` | Associate's degree |
| `BachelorDegree` | `ceterms:BachelorDegree` | Bachelor's degree |
| `Badge` | `ceterms:Badge` | Digital badge |
| `Certificate` | `ceterms:Certificate` | General certificate |
| `CertificateOfCompletion` | `ceterms:CertificateOfCompletion` | Completion certificate |
| `Certification` | `ceterms:Certification` | Professional certification |
| `Degree` | `ceterms:Degree` | General degree |
| `DigitalBadge` | `ceterms:DigitalBadge` | Digital badge credential |
| `Diploma` | `ceterms:Diploma` | Diploma credential |
| `DoctoralDegree` | `ceterms:DoctoralDegree` | General doctorate |
| `GeneralEducationDevelopment` | `ceterms:GeneralEducationDevelopment` | GED |
| `JourneymanCertificate` | `ceterms:JourneymanCertificate` | Journeyman completion |
| `License` | `ceterms:License` | Professional/occupational license |
| `MasterCertificate` | `ceterms:MasterCertificate` | Master craftsman certificate |
| `MasterDegree` | `ceterms:MasterDegree` | Master's degree |
| `MicroCredential` | `ceterms:MicroCredential` | Micro-credential |
| `ProfessionalDoctorate` | `ceterms:ProfessionalDoctorate` | Professional doctorate (JD, MD, etc.) |
| `QualityAssuranceCredential` | `ceterms:QualityAssuranceCredential` | QA credential |
| `ResearchDoctorate` | `ceterms:ResearchDoctorate` | Research doctorate (PhD, etc.) |
| `SecondarySchoolDiploma` | `ceterms:SecondarySchoolDiploma` | High school diploma |

---

## Appendix E: Data Quality Metrics

### Expected Coverage Rates

| Metric | Target | Formula |
|--------|--------|---------|
| Institution Coverage | 100% | IPEDS institutions with credentials / Total IPEDS institutions |
| Scorecard Match Rate | > 60% | Credentials with Scorecard data / Total credentials |
| BLS Wage Coverage | > 80% | Credentials with occupation wages / Total credentials |
| CIP Code Coverage | > 95% | CIP codes in crosswalk / CIP codes in completions |
| CE Match Rate | TBD | CE credentials matched to IPEDS / Total CE credentials |

### Validation Queries

```sql
-- Overall statistics
SELECT
  'total_credentials' as metric,
  COUNT(*) as value
FROM national_credentials_enriched

UNION ALL

SELECT
  'with_scorecard_earnings',
  COUNTIF(earnings_1yr_median IS NOT NULL)
FROM national_credentials_enriched

UNION ALL

SELECT
  'with_bls_wages',
  COUNTIF(primary_occupation_wage_median IS NOT NULL)
FROM national_credentials_enriched

UNION ALL

SELECT
  'unique_institutions',
  COUNT(DISTINCT unitid)
FROM national_credentials_enriched

UNION ALL

SELECT
  'unique_cip_codes',
  COUNT(DISTINCT cip_code)
FROM national_credentials_enriched

UNION ALL

SELECT
  'states_covered',
  COUNT(DISTINCT state)
FROM national_credentials_enriched;
```

---

*Document generated by Credential Atlas on December 14, 2025*
*Total documented fields: 229 across 6 tables*
*Implementation phases: 4 (Phase 4 pending CE API key)*
