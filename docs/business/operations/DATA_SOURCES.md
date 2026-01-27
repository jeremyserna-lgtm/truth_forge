# Credential Atlas Data Sources

## Source Documentation

This document describes all data sources ingested into Credential Atlas, their origins, schemas, and refresh patterns.

---

## Summary

| Source | Records | Format | Origin | Refresh |
|--------|---------|--------|--------|---------|
| Credential Engine Registry - Credentials | 193,490 | CSV | credentialfinder.org export | Manual |
| Credential Engine Registry - Learning Opportunities | 64,439 | CSV | credentialfinder.org export | Manual |
| Credential Engine Registry - Organizations | 24,635 | CSV | credentialfinder.org export | Manual |
| Credential Engine Registry - Assessments | 7,768 | CSV | credentialfinder.org export | Manual |
| IPEDS HD2023 (Institutions) | 6,163 | CSV | NCES Data Center | Annual |
| IPEDS C2023_a (Completions) | 303,292 | CSV | NCES Data Center | Annual |
| IPEDS IC2023 (Characteristics) | 6,049 | CSV | NCES Data Center | Annual |
| Texas ETPL | 6,550 | CSV | Texas Workforce Commission | Periodic |

**Total: ~606,000+ records**

---

## 1. Credential Engine Registry

### Source Information

| Attribute | Value |
|-----------|-------|
| Provider | Credential Engine |
| Website | https://credentialfinder.org |
| API Available | Yes (https://credentialengineregistry.org) |
| Export Method | Manual CSV export from Credential Finder |
| Data Standard | CTDL (Credential Transparency Description Language) |
| Coverage | United States |
| Update Frequency | Continuous (registry); exports are point-in-time |

### 1.1 Credentials Export

**File:** `registry_finder/credential Export.csv`
**Records:** 193,490
**Description:** All credentials published to the Credential Engine Registry including licenses, certifications, degrees, certificates, badges, and other credential types.

#### Schema

| Column | Description |
|--------|-------------|
| Row Type | Record type identifier (Resource) |
| CTID | Credential Transparency Identifier (globally unique) |
| CTDL Type | Schema type (e.g., ceterms:License, ceterms:Certification) |
| CTDL Type Label | Human-readable type (License, Certification, etc.) |
| Name | Credential name |
| Alternate Name(s) | Other names/abbreviations |
| Description | Full description of the credential |
| Credential Status Type | Active, Deprecated, etc. |
| Address | Physical address if applicable |
| Finder ID | Credential Finder internal ID |
| Identifier | External identifiers |
| In Language(s) | Language(s) of instruction/materials |
| Last Updated | Last modification date in registry |
| Owned By/Offered By | Issuing organization name |
| Published By | Organization that published to registry |
| Time Estimate(s) | Duration to complete |
| Industry Code(s) | NAICS codes |
| Occupation Code(s) | O*NET SOC codes |
| Instructional Program Code(s) | CIP codes |
| Learning Delivery Type(s) | Online, In-Person, Blended, etc. |
| Subject Webpage | URL for more information |
| Keywords | Searchable keywords |
| Provides Transfer Value For - Finder URL | Transfer/articulation relationships |
| Provides Transfer Value For Resource - Type | Type of transfer relationship |
| Provides Transfer Value For Resource - Name | Name of related credential |
| Provides Transfer Value For Resource - Description | Description of relationship |
| Provides Transfer Value For Resource - Provider - Name | Provider of related credential |
| Provides Transfer Value For Resource - Provider - Finder URL | URL to related provider |
| Financial Assistance | Available financial aid |
| Requirements Description(s) | Prerequisites in text |
| Requirements Condition(s) | Structured prerequisite conditions |
| Finder Detail Page | URL to Credential Finder page |
| Registry URI | Direct link to registry record |
| Required Credit | Credit requirements |
| Estimated Cost(s) | Cost information |
| Estimated Cost Details | Breakdown of costs |
| Outcomes Data Start Date | Outcomes data coverage start |
| Outcomes Data End Date | Outcomes data coverage end |
| Median average earnings... | Post-graduation earnings (where available) |
| Number of total students... | Credential earners count |
| Number of students who had post-graduation earnings... | Employment outcomes count |
| Programs with fewer than 10... | Suppression indicator |
| Percent and Number of Program Graduates | Graduate statistics |
| Unknown Outcome | Students with unknown outcomes |
| Median earnings of graduates... | 10-year earnings (PA data) |
| Percent of graduates who were employed... | 10-year employment rate (PA data) |

#### Key Identifiers

- **CTID**: Primary key, globally unique, format: `ce-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Finder ID**: Integer, Credential Finder internal
- **Registry URI**: Full URL to registry API resource

---

### 1.2 Learning Opportunities Export

**File:** `registry_finder/learningopportunity Export.csv`
**Records:** 64,439
**Description:** Programs, courses, and training pathways that prepare learners for credentials.

#### Schema

| Column | Description |
|--------|-------------|
| Row Type | Record type identifier |
| CTID | Credential Transparency Identifier |
| CTDL Type | ceterms:LearningOpportunityProfile |
| CTDL Type Label | Learning Opportunity |
| Name | Program/course name |
| Description | Full description |
| Life Cycle Status Type | Active, Ceased, etc. |
| Address | Location if applicable |
| Finder ID | Internal ID |
| Identifier | External identifiers |
| In Language(s) | Language of instruction |
| Last Updated | Last modification date |
| Owned By/Offered By | Provider organization |
| Published By | Publisher to registry |
| Time Estimate(s) | Duration (hours, weeks, etc.) |
| Industry Code(s) | NAICS codes |
| Occupation Code(s) | O*NET SOC codes |
| Instructional Program Code(s) | CIP codes |
| Delivery Type(s) | Delivery mode |
| Subject Webpage | URL |
| Keywords | Search terms |
| Financial Assistance | Aid available |
| Requirements Description(s) | Prerequisites |
| Requirements Condition(s) | Structured prerequisites |
| Finder Detail Page | Credential Finder URL |
| Registry URI | Registry API URL |
| Required Credit | Credit requirements |
| Estimated Cost(s) | Cost |
| Estimated Cost Details | Cost breakdown |

---

### 1.3 Organizations Export

**File:** `registry_finder/organization Export.csv`
**Records:** 24,635
**Description:** Organizations that issue credentials, provide training, or perform quality assurance.

#### Schema

| Column | Description |
|--------|-------------|
| Row Type | Record type identifier |
| CTID | Credential Transparency Identifier |
| CTDL Type | ceterms:CredentialOrganization or ceterms:QACredentialOrganization |
| CTDL Type Label | Credential Organization, QA Credential Organization |
| Name | Organization name |
| Alternate Name(s) | Other names/abbreviations |
| Description | Organization description |
| Life Cycle Status Type | Active, Ceased |
| Address | Physical address |
| Finder ID | Internal ID |
| Identifier | External identifiers (DUNS, FEIN, IPEDS, etc.) |
| Last Updated | Last modification date |
| Organization Type | Business, CredentialingOrganization, etc. |
| Sector Type | Public, Private For-Profit, Private Non-Profit |
| Published By | Publisher |
| Industry Code(s) | NAICS codes |
| Subject Webpage | Website |
| Keywords | Search terms |
| Finder Detail Page | Credential Finder URL |
| Registry URI | Registry API URL |

#### Linkage

- Can be linked to IPEDS via `Identifier` field (when IPEDS UNITID present)
- `CTID` links to credentials via `Owned By/Offered By` relationship

---

### 1.4 Assessments Export

**File:** `registry_finder/assessment Export.csv`
**Records:** 7,768
**Description:** Examinations, evaluations, and other assessments that verify competency or award credentials.

#### Schema

| Column | Description |
|--------|-------------|
| Row Type | Record type identifier |
| CTID | Credential Transparency Identifier |
| CTDL Type | ceterms:AssessmentProfile |
| CTDL Type Label | Assessment |
| Name | Assessment name |
| Description | Full description |
| Life Cycle Status Type | Active, Ceased |
| Address | Location if applicable |
| Finder ID | Internal ID |
| Identifier | External identifiers |
| In Language(s) | Language |
| Last Updated | Last modification date |
| Owned By/Offered By | Assessment provider |
| Time Estimate(s) | Duration |
| Industry Code(s) | NAICS codes |
| Occupation Code(s) | O*NET SOC codes |
| Instructional Program Code(s) | CIP codes |
| Delivery Type(s) | Online, In-Person, etc. |
| Subject Webpage | URL |
| Keywords | Search terms |
| Requirements Description(s) | Prerequisites |
| Requirements Condition(s) | Structured prerequisites |
| Finder Detail Page | Credential Finder URL |
| Registry URI | Registry API URL |
| Required Credit | Credit if applicable |
| Estimated Cost(s) | Exam fee |
| Estimated Cost Details | Fee breakdown |

---

## 2. IPEDS (Integrated Postsecondary Education Data System)

### Source Information

| Attribute | Value |
|-----------|-------|
| Provider | National Center for Education Statistics (NCES) |
| Website | https://nces.ed.gov/ipeds/ |
| Data Center | https://nces.ed.gov/ipeds/datacenter/ |
| Export Method | CSV download from Data Center |
| Coverage | All Title IV postsecondary institutions in US |
| Update Frequency | Annual (data year = prior academic year) |
| Current Data Year | 2023 |

---

### 2.1 HD2023 - Institutional Characteristics (Directory)

**File:** `ipeds/HD2023.csv`
**Records:** 6,163
**Description:** Directory information for every postsecondary institution including name, address, sector, Carnegie classification, and administrative contacts.

#### Schema (Key Columns)

| Column | Description |
|--------|-------------|
| UNITID | **Primary Key** - Unique institution identifier |
| INSTNM | Institution name |
| IALIAS | Institution alias/nickname |
| ADDR | Street address |
| CITY | City |
| STABBR | State abbreviation (2-letter) |
| ZIP | ZIP code |
| FIPS | FIPS state code |
| OBEREG | Bureau of Economic Analysis region |
| CHFNM | Chief administrator name |
| CHFTITLE | Chief administrator title |
| GENTELE | General phone number |
| EIN | Employer Identification Number |
| UEIS | Unique Entity Identifier |
| OPEID | Office of Postsecondary Education ID |
| OPEFLAG | OPE Title IV eligibility |
| WEBADDR | Institution website |
| ADMINURL | Admissions website |
| FAIDURL | Financial aid website |
| APPLURL | Application website |
| NPRICURL | Net price calculator URL |
| VETURL | Veterans services URL |
| ATHURL | Athletics website |
| DISAURL | Disability services URL |
| SECTOR | Sector (1-9 classification) |
| ICLEVEL | Level (4-year, 2-year, less-than-2-year) |
| CONTROL | Control (public, private nonprofit, private for-profit) |
| HLOFFER | Highest level of offering |
| UGOFFER | Undergraduate offering indicator |
| GROFFER | Graduate offering indicator |
| HDEGOFR1 | Highest degree offered |
| DEGGRANT | Degree-granting status |
| HBCU | Historically Black College/University |
| HOSPITAL | Has hospital |
| MEDICAL | Grants medical degree |
| TRIBAL | Tribal college |
| LOCALE | Locale code (urban/rural) |
| OPENPUBL | Open to public |
| ACT | Currently active |
| NEWID | New UNITID if merged |
| DEATHYR | Year closed (if applicable) |
| CLOSEDAT | Close date |
| CYACTIVE | Current year active |
| POSTSEC | Postsecondary indicator |
| C21BASIC | Carnegie 2021 Basic Classification |
| C18BASIC | Carnegie 2018 Basic Classification |
| INSTSIZE | Institution size category |
| CBSA | Core Based Statistical Area code |
| CBSATYPE | CBSA type (metro/micro) |
| CSA | Combined Statistical Area |
| COUNTYCD | County FIPS code |
| COUNTYNM | County name |
| CNGDSTCD | Congressional district |
| LONGITUD | Longitude |
| LATITUDE | Latitude |

#### Sector Codes

| Code | Description |
|------|-------------|
| 1 | Public, 4-year or above |
| 2 | Private nonprofit, 4-year or above |
| 3 | Private for-profit, 4-year or above |
| 4 | Public, 2-year |
| 5 | Private nonprofit, 2-year |
| 6 | Private for-profit, 2-year |
| 7 | Public, less-than-2-year |
| 8 | Private nonprofit, less-than-2-year |
| 9 | Private for-profit, less-than-2-year |

---

### 2.2 C2023_a - Completions by CIP, Award Level, and Demographics

**File:** `ipeds/C2023_a.csv`
**Records:** 303,292
**Description:** Number of awards/degrees conferred by institution, Classification of Instructional Programs (CIP) code, award level, and student demographics.

#### Schema

| Column | Description |
|--------|-------------|
| UNITID | Institution identifier (links to HD2023) |
| CIPCODE | 6-digit CIP code (program classification) |
| MAJORNUM | Major number (1 = first major, 2 = second major) |
| AWLEVEL | Award level code |
| CTOTALT | Total completers |
| CTOTALM | Total male completers |
| CTOTALW | Total female completers |
| CAIANT | American Indian/Alaska Native completers |
| CAIANM | American Indian/Alaska Native male |
| CAIANW | American Indian/Alaska Native female |
| CASIAT | Asian completers |
| CASIAM | Asian male |
| CASIAW | Asian female |
| CBKAAT | Black/African American completers |
| CBKAAM | Black/African American male |
| CBKAAW | Black/African American female |
| CHISPT | Hispanic/Latino completers |
| CHISPM | Hispanic/Latino male |
| CHISPW | Hispanic/Latino female |
| CNHPIT | Native Hawaiian/Pacific Islander completers |
| CNHPIM | Native Hawaiian/Pacific Islander male |
| CNHPIW | Native Hawaiian/Pacific Islander female |
| CWHITT | White completers |
| CWHITM | White male |
| CWHITW | White female |
| C2MORT | Two or more races completers |
| C2MORM | Two or more races male |
| C2MORW | Two or more races female |
| CUNKNT | Race/ethnicity unknown completers |
| CUNKNM | Race/ethnicity unknown male |
| CUNKNW | Race/ethnicity unknown female |
| CNRALT | Nonresident alien completers |
| CNRALM | Nonresident alien male |
| CNRALW | Nonresident alien female |

Note: Columns prefixed with `X` (e.g., `XCTOTALT`) contain imputation flags.

#### Award Level Codes (AWLEVEL)

| Code | Description |
|------|-------------|
| 1 | Postsecondary award, certificate, or diploma (less than 1 year) |
| 2 | Postsecondary award, certificate, or diploma (1-2 years) |
| 3 | Associate's degree |
| 4 | Postsecondary award, certificate, or diploma (2-4 years) |
| 5 | Bachelor's degree |
| 6 | Postbaccalaureate certificate |
| 7 | Master's degree |
| 8 | Post-master's certificate |
| 9 | Doctor's degree - research/scholarship |
| 10 | Doctor's degree - professional practice |
| 11 | Doctor's degree - other |
| 12 | Other |

---

### 2.3 IC2023 - Institutional Characteristics

**File:** `ipeds/IC2023.csv`
**Records:** 6,049
**Description:** Institutional characteristics including mission, calendar system, program offerings, and services.

#### Schema (Key Columns)

| Column | Description |
|--------|-------------|
| UNITID | Institution identifier |
| PEO1ISTR - PEO7ISTR | Primary educational offerings |
| CNTLAFFI | Control/affiliation |
| PUBPRIME | Public institution primary source of control |
| PUBSECON | Public institution secondary source of control |
| RELAFFIL | Religious affiliation |
| LEVEL1 - LEVEL19 | Program levels offered |
| CALSYS | Calendar system |
| FT_UG | Full-time undergraduates |
| FT_FTUG | First-time full-time undergraduates |
| FTGDNIDP | Full-time graduate non-degree |

---

## 3. State Workforce Data

### 3.1 Texas ETPL (Eligible Training Provider List)

**File:** `texas_etpl_raw.csv`
**Records:** 6,550
**Description:** Texas Workforce Commission's list of approved training providers and programs eligible for WIOA funding.

#### Source Information

| Attribute | Value |
|-----------|-------|
| Provider | Texas Workforce Commission (TWC) |
| Website | https://www.twc.texas.gov |
| Export Method | Manual download from TWC portal |
| Coverage | Texas only |
| Update Frequency | Periodic (quarterly typical) |

#### Schema

| Column | Description |
|--------|-------------|
| Provider Name | Training provider organization name |
| Description Of Provider | Provider description |
| Provider URL | Provider website |
| Campus Name | Specific campus/location name |
| Campus Address1 | Street address line 1 |
| Campus Address2 | Street address line 2 |
| Campus City | City |
| Campus State | State (TX) |
| Campus Zip Code | ZIP code |
| Campus County | County |
| Program Name | Training program name |
| Program Description | Program description |
| Length: Contact Hours | Program duration in contact hours |
| Length: Weeks | Program duration in weeks |
| Program Format | Delivery mode (In-Person, Online, Hybrid) |
| Required Cost | Total program cost |

#### Notes

- All 50 states maintain ETPL lists as required by WIOA
- Format and fields vary by state
- Typically includes WIOA-approved providers only
- May not include all credentials offered by listed providers

---

## 4. Internal/Demo Data

### 4.1 Demo Credentials

**File:** `demo_credentials.jsonl`
**Records:** 3
**Description:** Sample credential records in Credential Atlas internal schema for testing and demonstration.

#### Schema

```json
{
  "id": "string (UUID)",
  "ctid": "string (nullable, CTDL ID if from registry)",
  "name": "string",
  "description": "string",
  "credential_type": "string (certification|certificate|license|degree|badge)",
  "cip_code": "string (nullable)",
  "provider_id": "string (nullable)",
  "provider_name": "string",
  "provider_state": "string (2-letter)",
  "cost": {
    "amount": "number",
    "currency": "string (USD)",
    "description": "string",
    "includes_fees": "boolean"
  },
  "duration": {
    "value": "number",
    "unit": "string (weeks|months|hours|years)",
    "description": "string"
  },
  "delivery_mode": "string (online|in_person|hybrid)",
  "subject_webpage": "string (URL, nullable)",
  "occupation_alignments": ["array of O*NET codes"],
  "industry_codes": ["array of NAICS codes"],
  "keywords": ["array of strings"],
  "prerequisite_credentials": ["array of credential IDs"],
  "prerequisite_description": "string (nullable)",
  "data_source": "string (manual|scraped|api|state_doe)",
  "source_url": "string (nullable)",
  "last_verified": "string (ISO date, nullable)",
  "confidence_score": "number (0-1)",
  "ctdl_raw": "object (nullable, raw CTDL if from registry)"
}
```

---

## 5. State Assessments

### 5.1 Texas State Assessment

**File:** `assessments/TX_state0.json` + `assessments/TX_state0_report.md`
**Description:** Comprehensive assessment of Texas credential landscape including policy, education, workforce, and data source analysis.

#### Contents

- Executive summary with key metrics
- Policy landscape (governance, agencies, transparency)
- Education landscape (institutions by type)
- Workforce landscape (employment, industries)
- Outcomes data infrastructure
- Data source inventory
- Integration priorities
- Phased ingestion plan

---

## Linkage Keys

### Primary Keys by Source

| Source | Primary Key | Format |
|--------|-------------|--------|
| Credential Engine | CTID | `ce-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| IPEDS | UNITID | 6-digit integer |
| Texas ETPL | Provider Name + Program Name | Composite string |
| Internal | id | UUID hex string |

### Cross-Source Linkage

| From | To | Via |
|------|-----|-----|
| Credential Engine Credentials | Credential Engine Organizations | Owned By/Offered By |
| Credential Engine Organizations | IPEDS | Identifier (when IPEDS UNITID present) |
| IPEDS Completions | IPEDS Institutions | UNITID |
| IPEDS Completions | Credential Types | AWLEVEL |
| Any Source | Programs/Credentials | CIP Code (CIPCODE / Instructional Program Code) |
| Any Source | Occupations | O*NET SOC Code |
| Any Source | Industries | NAICS Code |

---

## Data Quality Notes

### Credential Engine Registry
- Coverage varies by state and credential type
- Organizations self-publish; quality depends on publisher
- Some records incomplete (missing costs, duration, etc.)
- CTID is authoritative; other IDs may not be present

### IPEDS
- Comprehensive for Title IV institutions
- Does not include non-Title-IV providers
- Annual data; 1-2 year lag from current
- Completions data granular by CIP but not by specific credential name

### State ETPL
- Only includes WIOA-approved providers
- Formats vary significantly by state
- May not include all programs at listed providers
- Update frequency varies by state

---

## Refresh Schedule

| Source | Current Version | Next Expected | Method |
|--------|-----------------|---------------|--------|
| Credential Engine Registry | Jan 2026 | Continuous | API or manual export |
| IPEDS | 2023 | Fall 2026 (2024 data) | NCES Data Center |
| Texas ETPL | Dec 2025 | Q1 2026 | TWC portal |

---

*Last Updated: January 2026*
