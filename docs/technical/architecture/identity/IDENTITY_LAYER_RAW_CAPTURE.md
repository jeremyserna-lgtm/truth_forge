# Identity Layer - Raw Capture Design

**Version**: 1.0.0
**Date**: 2025-12-08
**Status**: Raw Capture Design
**Owner**: Jeremy Serna

---

## Overview

This document defines the **raw capture layer** for the identity system. The Apple Contacts database is extracted and stored in its **pure, unmodified form** in BigQuery. **NO parsing, processing, or transformation occurs** - this is purely a data capture operation.

### Two-Stage Process

1. **Stage 1: Raw Capture** (This Document) - **PURE CAPTURE ONLY**
   - Extract Apple Contacts SQLite data as-is
   - Store in raw capture tables exactly as it appears in source
   - Track extraction metadata
   - **NO parsing, NO processing, NO transformation, NO business logic**
   - Preserve data purity for future processing

2. **Stage 2: Parse & Operationalize** (Separate Process - Not This Document)
   - Parse raw capture data (separate scripts/tables)
   - Transform into structured tables (`contacts_master`, `contact_identifiers`, etc.)
   - Apply business logic and categorization
   - **This happens AFTER raw capture is complete**

---

## Raw Capture Tables

### 1. `identity.raw_apple_contacts_records`

**Purpose**: Store raw contact records from `ZABCDRECORD` table

**Schema**:
```sql
CREATE TABLE `identity.raw_apple_contacts_records` (
  -- Extraction Metadata
  extraction_id STRING NOT NULL,                -- Unique extraction run ID
  extraction_timestamp TIMESTAMP NOT NULL,      -- When extracted
  source_file_path STRING NOT NULL,              -- Path to .abcddb file
  source_database_id STRING NOT NULL,            -- Source database identifier

  -- Apple Contacts Primary Key
  apple_contact_pk INT64 NOT NULL,              -- Z_PK from Apple Contacts

  -- Apple Contacts Identifiers
  apple_unique_id STRING,                        -- ZUNIQUEID
  apple_identity_unique_id STRING,              -- ZIDENTITYUNIQUEID
  apple_link_id STRING,                         -- ZLINKID

  -- Core Data Fields (All Apple Contacts Fields)
  entity_type INT64,                             -- Z_ENT
  record_type INT64,                             -- ZTYPE
  ios_legacy_identifier INT64,                  -- ZIOSLEGACYIDENTIFIER

  -- Name Fields
  first_name STRING,                             -- ZFIRSTNAME
  last_name STRING,                              -- ZLASTNAME
  middle_name STRING,                            -- ZMIDDLENAME
  nickname STRING,                               -- ZNICKNAME
  name_suffix STRING,                            -- ZSUFFIX
  title STRING,                                  -- ZTITLE
  full_name STRING,                              -- ZNAME
  name_normalized STRING,                        -- ZNAMENORMALIZED
  sorting_first_name STRING,                     -- ZSORTINGFIRSTNAME
  sorting_last_name STRING,                      -- ZSORTINGLASTNAME
  phonetic_first_name STRING,                    -- ZPHONETICFIRSTNAME
  phonetic_last_name STRING,                     -- ZPHONETICLASTNAME
  phonetic_middle_name STRING,                   -- ZPHONETICMIDDLENAME
  maiden_name STRING,                            -- ZMAIDENNAME

  -- Organization Fields
  organization STRING,                           -- ZORGANIZATION
  phonetic_organization STRING,                  -- ZPHONETICORGANIZATION
  job_title STRING,                              -- ZJOBTITLE
  department STRING,                              -- ZDEPARTMENT

  -- Dates
  birthday TIMESTAMP,                            -- ZBIRTHDAY
  birthday_year INT64,                           -- ZBIRTHDAYYEAR
  birthday_yearless FLOAT64,                     -- ZBIRTHDAYYEARLESS
  creation_date TIMESTAMP,                       -- ZCREATIONDATE
  creation_date_year INT64,                     -- ZCREATIONDATEYEAR
  creation_date_yearless FLOAT64,                -- ZCREATIONDATEYEARLESS
  modification_date TIMESTAMP,                   -- ZMODIFICATIONDATE
  modification_date_year INT64,                  -- ZMODIFICATIONDATEYEAR
  modification_date_yearless FLOAT64,            -- ZMODIFICATIONDATEYEARLESS
  last_sync_date TIMESTAMP,                      -- ZLASTSYNCDATE

  -- Flags and Status
  is_me BOOL,                                    -- ZME (contact is "me")
  display_flags INT64,                           -- ZDISPLAYFLAGS
  sync_status INT64,                             -- ZSYNCSTATUS
  privacy_flags INT64,                           -- ZPRIVACYFLAGS
  guardian_flags INT64,                          -- ZGUARDIANFLAGS
  preferred_for_link_name INT64,                 -- ZPREFERREDFORLINKNAME
  preferred_for_link_photo INT64,                -- ZPREFERREDFORLINKPHOTO

  -- Container and Grouping
  container_id INT64,                            -- ZCONTAINER
  container_1_id INT64,                          -- ZCONTAINER1
  container_2_id INT64,                          -- ZCONTAINER2
  container_where_contact_is_me INT64,           -- ZCONTAINERWHERECONTACTISME
  external_group_behavior INT64,                 -- ZEXTERNALGROUPBEHAVIOR

  -- Indexing and Search
  contact_index_id INT64,                       -- ZCONTACTINDEX
  search_element_data BYTES,                     -- ZSEARCHELEMENTDATA

  -- Image and Media
  image_reference STRING,                        -- ZIMAGEREFERENCE
  image_type STRING,                             -- ZIMAGETYPE
  image_data BYTES,                              -- ZIMAGEDATA
  image_hash BYTES,                              -- ZIMAGEHASH
  thumbnail_image_data BYTES,                    -- ZTHUMBNAILIMAGEDATA
  avatar_recipe_data BYTES,                      -- ZAVATARRECIPEDATA
  crop_rect STRING,                              -- ZCROPRECT
  crop_rect_id STRING,                           -- ZCROPRECTID
  crop_rect_hash BYTES,                          -- ZCROPRECTHASH
  wallpaper_uri STRING,                         -- ZWALLPAPERURI
  wallpaper BYTES,                               -- ZWALLPAPER
  memoji_metadata BYTES,                         -- ZMEMOJIMETADATA

  -- External and Sync
  external_uri STRING,                           -- ZEXTERNALURI
  external_uuid STRING,                          -- ZEXTERNALUUID
  external_filename STRING,                      -- ZEXTERNALFILENAME
  external_hash STRING,                           -- ZEXTERNALHASH
  external_collection_path STRING,               -- ZEXTERNALCOLLECTIONPATH
  external_image_uri STRING,                     -- ZEXTERNALIMAGEURI
  external_modification_tag STRING,              -- ZEXTERNALMODIFICATIONTAG
  external_identifier STRING,                    -- ZEXTERNALIDENTIFIER
  remote_location STRING,                        -- ZREMOTELOCATION
  provider_identifier STRING,                    -- ZPROVIDERIDENTIFIER
  provider_metadata_id INT64,                   -- ZPROVIDERMETADATA
  sync_anchor STRING,                            -- ZSYNCANCHOR
  assistant_sync_anchor_id INT64,                -- ZASSISTANTSYNCANCHOR
  share_count INT64,                             -- ZSHARECOUNT
  sync_count INT64,                              -- ZSYNCCOUNT
  version INT64,                                 -- ZVERSION

  -- Additional Fields
  note_id INT64,                                 -- ZNOTE (reference to note table)
  lunar_birthday_components_id INT64,            -- ZLUNARBIRTHDAYCOMPONENTS
  date_components_id INT64,                      -- ZDATECOMPONENTS
  info_id INT64,                                 -- ZINFO
  is_all INT64,                                  -- ZISALL

  -- String Fields
  name_1 STRING,                                 -- ZNAME1
  tmp_remote_location STRING,                    -- ZTMPREMOTELOCATION
  tmp_homepage STRING,                           -- ZTMPHOMEPAGE
  phone_media_data STRING,                       -- ZPHONEMEDATA
  assistant_validity STRING,                     -- ZASSISTANTVALIDITY
  created_version STRING,                        -- ZCREATEDVERSION
  last_saved_version STRING,                     -- ZLASTSAVEDVERSION
  last_dot_mac_account STRING,                   -- ZLASTDOTMACACCOUNT
  preferred_apple_persona_identifier STRING,     -- ZPREFERREDAPPLEPERSONAIDENTIFIER
  preferred_likeness_source STRING,               -- ZPREFERREDLIKENESSSOURCE
  serial_number STRING,                          -- ZSERIALNUMBER
  downtime_whitelist STRING,                     -- ZDOWNTIMEWHITELIST

  -- Binary Fields
  external_representation BYTES,                 -- ZEXTERNALREPRESENTATION
  modified_unique_ids_data BYTES,                -- ZMODIFIEDUNIQUEIDSDATA
  sensitive_content_configuration BYTES,         -- ZSENSITIVECONTENTCONFIGURATION

  -- Timestamps
  images_sync_failed_time TIMESTAMP,             -- ZIMAGESYNCFAILEDTIME
  wallpapers_sync_failed_time TIMESTAMP,        -- ZWALLPAPERSYNCFAILEDTIME

  -- Raw Data Preservation
  raw_record_json JSON,                          -- Complete record as JSON for reference

  PRIMARY KEY (extraction_id, apple_contact_pk, source_database_id),
  INDEX (extraction_id),
  INDEX (apple_unique_id),
  INDEX (apple_identity_unique_id),
  INDEX (apple_link_id),
  INDEX (extraction_timestamp)
)
PARTITION BY DATE(extraction_timestamp)
CLUSTER BY extraction_id, entity_type;
```

### 2. `identity.raw_apple_contacts_phone_numbers`

**Purpose**: Store raw phone numbers from `ZABCDPHONENUMBER` table

**Schema**:
```sql
CREATE TABLE `identity.raw_apple_contacts_phone_numbers` (
  -- Extraction Metadata
  extraction_id STRING NOT NULL,
  extraction_timestamp TIMESTAMP NOT NULL,
  source_file_path STRING NOT NULL,
  source_database_id STRING NOT NULL,

  -- Apple Contacts Primary Keys
  apple_phone_pk INT64 NOT NULL,                -- Z_PK from ZABCDPHONENUMBER
  apple_contact_pk INT64 NOT NULL,              -- ZOWNER (FK to ZABCDRECORD)

  -- Phone Number Data
  full_number STRING,                            -- ZFULLNUMBER
  country_code STRING,                           -- ZCOUNTRYCODE
  area_code STRING,                              -- ZAREACODE
  local_number STRING,                           -- ZLOCALNUMBER
  extension STRING,                              -- ZEXTENSION
  last_four_digits STRING,                       -- ZLASTFOURDIGITS

  -- Metadata
  label STRING,                                  -- ZLABEL (Mobile, Work, Home, etc.)
  is_primary BOOL,                               -- ZISPRIMARY
  is_private BOOL,                               -- ZISPRIVATE
  ordering_index INT64,                          -- ZORDERINGINDEX
  ios_legacy_identifier INT64,                   -- ZIOSLEGACYIDENTIFIER
  unique_id STRING,                              -- ZUNIQUEID

  -- Raw Data Preservation
  raw_record_json JSON,                          -- Complete record as JSON

  PRIMARY KEY (extraction_id, apple_phone_pk, source_database_id),
  FOREIGN KEY (extraction_id, apple_contact_pk, source_database_id)
    REFERENCES identity.raw_apple_contacts_records(extraction_id, apple_contact_pk, source_database_id),
  INDEX (extraction_id),
  INDEX (apple_contact_pk),
  INDEX (full_number),
  INDEX (is_primary)
)
PARTITION BY DATE(extraction_timestamp)
CLUSTER BY extraction_id, apple_contact_pk;
```

### 3. `identity.raw_apple_contacts_email_addresses`

**Purpose**: Store raw email addresses from `ZABCDEMAILADDRESS` table

**Schema**:
```sql
CREATE TABLE `identity.raw_apple_contacts_email_addresses` (
  -- Extraction Metadata
  extraction_id STRING NOT NULL,
  extraction_timestamp TIMESTAMP NOT NULL,
  source_file_path STRING NOT NULL,
  source_database_id STRING NOT NULL,

  -- Apple Contacts Primary Keys
  apple_email_pk INT64 NOT NULL,                 -- Z_PK from ZABCDEMAILADDRESS
  apple_contact_pk INT64 NOT NULL,              -- ZOWNER (FK to ZABCDRECORD)

  -- Email Data
  email_address STRING,                          -- ZADDRESS
  email_normalized STRING,                       -- ZADDRESSNORMALIZED

  -- Metadata
  label STRING,                                  -- ZLABEL (Work, Home, etc.)
  is_primary BOOL,                               -- ZISPRIMARY
  is_private BOOL,                               -- ZISPRIVATE
  ordering_index INT64,                          -- ZORDERINGINDEX
  ios_legacy_identifier INT64,                   -- ZIOSLEGACYIDENTIFIER
  unique_id STRING,                              -- ZUNIQUEID

  -- Raw Data Preservation
  raw_record_json JSON,                          -- Complete record as JSON

  PRIMARY KEY (extraction_id, apple_email_pk, source_database_id),
  FOREIGN KEY (extraction_id, apple_contact_pk, source_database_id)
    REFERENCES identity.raw_apple_contacts_records(extraction_id, apple_contact_pk, source_database_id),
  INDEX (extraction_id),
  INDEX (apple_contact_pk),
  INDEX (email_address),
  INDEX (email_normalized),
  INDEX (is_primary)
)
PARTITION BY DATE(extraction_timestamp)
CLUSTER BY extraction_id, apple_contact_pk;
```

### 4. `identity.raw_apple_contacts_social_profiles`

**Purpose**: Store raw social profiles from `ZABCDSOCIALPROFILE` table

**Schema**:
```sql
CREATE TABLE `identity.raw_apple_contacts_social_profiles` (
  -- Extraction Metadata
  extraction_id STRING NOT NULL,
  extraction_timestamp TIMESTAMP NOT NULL,
  source_file_path STRING NOT NULL,
  source_database_id STRING NOT NULL,

  -- Apple Contacts Primary Keys
  apple_social_pk INT64 NOT NULL,                -- Z_PK from ZABCDSOCIALPROFILE
  apple_contact_pk INT64 NOT NULL,              -- ZOWNER (FK to ZABCDRECORD)

  -- Social Profile Data
  service_name STRING,                           -- ZSERVICENAME (Instagram, Facebook, etc.)
  username STRING,                               -- ZUSERNAME
  user_identifier STRING,                        -- ZUSERIDENTIFIER
  url_string STRING,                             -- ZURLSTRING
  display_name STRING,                           -- ZDISPLAYNAME

  -- Metadata
  label STRING,                                  -- ZLABEL
  is_primary BOOL,                               -- ZISPRIMARY
  is_private BOOL,                               -- ZISPRIVATE
  ordering_index INT64,                          -- ZORDERINGINDEX
  ios_legacy_identifier INT64,                   -- ZIOSLEGACYIDENTIFIER
  unique_id STRING,                              -- ZUNIQUEID
  bundle_identifiers_string STRING,              -- ZBUNDLEIDENTIFIERSSTRING
  team_identifier STRING,                        -- ZTEAMIDENTIFIER

  -- Binary Data
  custom_values_data BYTES,                      -- ZCUSTOMVALUESDATA

  -- Raw Data Preservation
  raw_record_json JSON,                          -- Complete record as JSON

  PRIMARY KEY (extraction_id, apple_social_pk, source_database_id),
  FOREIGN KEY (extraction_id, apple_contact_pk, source_database_id)
    REFERENCES identity.raw_apple_contacts_records(extraction_id, apple_contact_pk, source_database_id),
  INDEX (extraction_id),
  INDEX (apple_contact_pk),
  INDEX (service_name),
  INDEX (username)
)
PARTITION BY DATE(extraction_timestamp)
CLUSTER BY extraction_id, apple_contact_pk;
```

### 5. `identity.raw_apple_contacts_notes`

**Purpose**: Store raw notes from `ZABCDNOTE` table

**Schema**:
```sql
CREATE TABLE `identity.raw_apple_contacts_notes` (
  -- Extraction Metadata
  extraction_id STRING NOT NULL,
  extraction_timestamp TIMESTAMP NOT NULL,
  source_file_path STRING NOT NULL,
  source_database_id STRING NOT NULL,

  -- Apple Contacts Primary Keys
  apple_note_pk INT64 NOT NULL,                 -- Z_PK from ZABCDNOTE
  apple_contact_pk INT64 NOT NULL,              -- ZCONTACT (FK to ZABCDRECORD)

  -- Note Data
  note_text STRING,                              -- ZTEXT
  rich_text_data BYTES,                          -- ZRICHTEXTDATA

  -- Raw Data Preservation
  raw_record_json JSON,                          -- Complete record as JSON

  PRIMARY KEY (extraction_id, apple_note_pk, source_database_id),
  FOREIGN KEY (extraction_id, apple_contact_pk, source_database_id)
    REFERENCES identity.raw_apple_contacts_records(extraction_id, apple_contact_pk, source_database_id),
  INDEX (extraction_id),
  INDEX (apple_contact_pk)
)
PARTITION BY DATE(extraction_timestamp)
CLUSTER BY extraction_id, apple_contact_pk;
```

### 6. `identity.raw_apple_contacts_extractions`

**Purpose**: Track extraction runs and metadata

**Schema**:
```sql
CREATE TABLE `identity.raw_apple_contacts_extractions` (
  extraction_id STRING NOT NULL,                 -- Unique extraction run ID
  extraction_timestamp TIMESTAMP NOT NULL,        -- When extraction started
  extraction_completed_at TIMESTAMP,              -- When extraction completed
  extraction_status STRING NOT NULL,              -- in_progress, completed, failed

  -- Source Information
  source_archive_path STRING NOT NULL,           -- Path to .abbu archive
  source_databases ARRAY<STRUCT<
    database_id STRING,
    database_path STRING,
    database_size_bytes INT64,
    contacts_count INT64,
    phones_count INT64,
    emails_count INT64,
    social_profiles_count INT64,
    notes_count INT64
  >>,

  -- Extraction Statistics
  total_contacts_extracted INT64,
  total_phones_extracted INT64,
  total_emails_extracted INT64,
  total_social_profiles_extracted INT64,
  total_notes_extracted INT64,

  -- Validation
  extraction_validated BOOL DEFAULT FALSE,
  validation_errors ARRAY<STRING>,
  validation_warnings ARRAY<STRING>,

  -- Metadata
  extraction_method STRING,                       -- sqlite_export, api, etc.
  extraction_script_version STRING,
  extraction_config JSON,                         -- Configuration used

  -- Error Handling
  error_message STRING,
  error_stack_trace STRING,

  PRIMARY KEY (extraction_id),
  INDEX (extraction_timestamp),
  INDEX (extraction_status)
)
PARTITION BY DATE(extraction_timestamp)
CLUSTER BY extraction_id, extraction_status;
```

---

## Extraction Granularity and Deduplication

### Entity-Level Extraction

The extraction operates at the **entity level** (individual contacts, phones, emails, etc.), NOT at the dataset level. This enables:

1. **Deduplication**: Skip unchanged entities between extractions
2. **Incremental Updates**: Only extract new or modified entities
3. **Change Tracking**: Track what changed between extractions
4. **Efficient Storage**: Avoid storing duplicate data

### Deduplication Strategy

**Key**: Use `apple_unique_id` + `modification_date` to detect changes

**Process**:
1. For each entity in source database:
   - Check if `apple_unique_id` exists in previous extraction
   - Compare `modification_date` with previous extraction
   - If `modification_date` is newer OR entity doesn't exist → Extract
   - If `modification_date` is same or older → Skip (unchanged)

**Benefits**:
- Reduces data volume (only changed entities)
- Faster extractions (skip unchanged records)
- Preserves change history (each extraction_id captures state at that time)
- Enables incremental processing

### Extraction Modes

1. **Full Extraction** (First Run)
   - Extract ALL entities regardless of modification_date
   - No deduplication (nothing to compare against)
   - Establishes baseline

2. **Incremental Extraction** (Subsequent Runs)
   - Extract only new or modified entities
   - Deduplicate against previous extraction
   - Track what changed

## Extraction Process

**CRITICAL**: This process is **PURE CAPTURE ONLY**. No parsing, processing, or transformation.

### Step 1: Initialize Extraction

1. Generate unique `extraction_id` (e.g., `extract_apple_contacts_20251208_001`)
2. Record extraction start in `raw_apple_contacts_extractions`
3. Scan source archive for all `.abcddb` files
4. Identify source databases and record metadata
5. **Determine extraction mode**: Full or Incremental
6. **NO filtering, NO transformation, NO business logic**

### Step 2: Extract Records (Pure Read & Write with Deduplication)

For each source database:

1. **Get Previous Extraction State** (for incremental mode)
   - Query latest extraction for this `source_database_id`
   - Get `apple_unique_id` + `modification_date` for all entities
   - Build change detection map

2. **Extract Contact Records** (`ZABCDRECORD`)
   - **Read ALL records** (no filtering by `Z_ENT` or `ZTYPE`)
   - **For each record**:
     - Check if `apple_unique_id` exists in previous extraction
     - Compare `modification_date` with previous
     - **If new or modified**: Extract (write to BigQuery)
     - **If unchanged**: Skip (deduplicate)
   - **Extract ALL fields exactly as they appear** in SQLite
   - **Write directly to BigQuery** without modification
   - Store complete record as JSON for reference
   - **NO field mapping, NO data type conversion beyond SQLite → BigQuery basics**

3. **Extract Phone Numbers** (`ZABCDPHONENUMBER`)
   - **Read ALL phone number records**
   - **For each record**:
     - Check if `unique_id` exists in previous extraction
     - Compare `ZOWNER` (contact) modification_date
     - **If contact modified or phone new**: Extract
     - **If unchanged**: Skip
   - **Extract ALL fields exactly as they appear**
   - **Write directly to BigQuery** without modification
   - **NO normalization, NO formatting, NO validation**

4. **Extract Email Addresses** (`ZABCDEMAILADDRESS`)
   - **Read ALL email records**
   - **For each record**:
     - Check if `unique_id` exists in previous extraction
     - Compare `ZOWNER` (contact) modification_date
     - **If contact modified or email new**: Extract
     - **If unchanged**: Skip
   - **Extract ALL fields exactly as they appear**
   - **Write directly to BigQuery** without modification
   - **NO normalization, NO validation**

5. **Extract Social Profiles** (`ZABCDSOCIALPROFILE`)
   - **Read ALL social profile records**
   - **For each record**:
     - Check if `unique_id` exists in previous extraction
     - Compare `ZOWNER` (contact) modification_date
     - **If contact modified or profile new**: Extract
     - **If unchanged**: Skip
   - **Extract ALL fields exactly as they appear**
   - **Write directly to BigQuery** without modification

6. **Extract Notes** (`ZABCDNOTE`)
   - **Read ALL note records**
   - **For each record**:
     - Check if `Z_PK` exists in previous extraction
     - Compare `ZCONTACT` (contact) modification_date
     - **If contact modified or note new**: Extract
     - **If unchanged**: Skip
   - **Extract ALL fields exactly as they appear**
   - **Write directly to BigQuery** without modification

### Step 3: Validate Extraction (Counts Only)

1. **Count records extracted** vs. source (for verification)
2. **Count records skipped** (deduplicated)
3. **NO data validation, NO business logic, NO relationship checking**
4. Record extraction statistics (counts only)

### Step 4: Complete Extraction

1. Update `raw_apple_contacts_extractions` with completion status
2. Record extraction statistics (extracted + skipped counts)
3. Mark extraction as complete
4. **NO data quality checks, NO transformation, NO processing**

---

## Extraction Script Structure

```python
"""
Apple Contacts Raw Extraction Script

Extracts Apple Contacts database (.abcddb) files and stores in BigQuery
raw capture tables without any transformation.

Uses central services:
- Run service: get_current_run_id() for run tracking
- Log service: get_logger() for structured logging
- Cost service: track_cost() for BigQuery cost tracking
- ID service: generate_run_id() for extraction IDs
- BigQuery client: get_bigquery_client() for BigQuery operations
- Governance: record_audit() for audit trail
"""

from datetime import datetime
from pathlib import Path
import os
import sqlite3
import json
from typing import Dict, List, Any

# Central Services Imports
from architect_central_services import (
    get_logger,
    get_current_run_id,
    get_correlation_ids,
    track_cost,
    get_bigquery_client,
    generate_run_id,
)
from architect_central_services.governance.governance_service.unified_governance import (
    get_unified_governance,
)
from architect_central_services.governance.pre_run_validator import validate_before_run

logger = get_logger(__name__)

def extract_apple_contacts_raw(
    contacts_db_path: str = None,
    project_id: str = "flash-clover-464719-g1",
    dataset_id: str = "identity"
) -> str:
    """Extract Apple Contacts database to raw capture tables.

    PURE CAPTURE ONLY - No parsing, processing, or transformation.

    Args:
        contacts_db_path: Path to Apple Contacts database directory
                         Default: ~/Library/Application Support/AddressBook/
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID

    Returns:
        extraction_id: Unique extraction run ID
    """
    # Pre-run validation
    validate_before_run()

    # Get run context
    run_id = get_current_run_id()
    correlation_ids = get_correlation_ids()

    # Default to macOS Contacts database location
    if contacts_db_path is None:
        contacts_db_path = os.path.expanduser("~/Library/Application Support/AddressBook/")

    # Generate extraction ID using central service
    extraction_id = f"extract_apple_contacts_{generate_run_id()}"
    extraction_timestamp = datetime.now()

    logger.info(
        "Starting Apple Contacts raw extraction",
        extra={
            "run_id": run_id,
            "extraction_id": extraction_id,
            "contacts_db_path": contacts_db_path,
            "project_id": project_id,
            "dataset_id": dataset_id,
            "correlation_ids": correlation_ids,
        }
    )

    # Initialize BigQuery client using central service
    bq_client = get_bigquery_client(project_id=project_id)

    # Initialize governance service for audit trail
    governance = get_unified_governance()

    # Record extraction start in audit trail
    governance.record_audit(
        category="data_extraction",
        level="info",
        operation="extract_apple_contacts_raw",
        component="identity_raw_capture",
        agent="system",
        action="extraction_started",
        success=True,
        context={
            "extraction_id": extraction_id,
            "contacts_db_path": contacts_db_path,
            "run_id": run_id,
        }
    )

    # macOS Contacts Database Location
    # Default: ~/Library/Application Support/AddressBook/
    # This is the live, active Contacts database on macOS
    # Structure:
    #   - AddressBook-v22.abcddb (main database)
    #   - Sources/{UUID}/AddressBook-v22.abcddb (source-specific databases)

    # Record extraction start in tracking table
    record_extraction_start(
        bq_client, dataset_id, extraction_id, extraction_timestamp,
        contacts_db_path, run_id
    )

    # Find all source databases in the Contacts directory
    source_databases = find_source_databases(contacts_db_path)

    logger.info(
        f"Found {len(source_databases)} source databases",
        extra={
            "run_id": run_id,
            "extraction_id": extraction_id,
            "database_count": len(source_databases),
        }
    )

    # Extract from each database
    total_stats = {
        'contacts': {'extracted': 0, 'skipped': 0},
        'phones': {'extracted': 0, 'skipped': 0},
        'emails': {'extracted': 0, 'skipped': 0},
        'social_profiles': {'extracted': 0, 'skipped': 0},
        'notes': {'extracted': 0, 'skipped': 0},
        'extraction_modes': []
    }

    for db_info in source_databases:
        db_path = db_info['path']
        db_id = db_info['id']

        logger.info(
            f"Extracting from database: {db_id}",
            extra={
                "run_id": run_id,
                "extraction_id": extraction_id,
                "database_id": db_id,
                "database_path": db_path,
            }
        )

        # Extract records (pure capture only, with deduplication)
        stats = extract_database(
            bq_client, dataset_id, extraction_id, extraction_timestamp,
            db_path, db_id, run_id
        )

        # Accumulate stats
        for key in ['contacts', 'phones', 'emails', 'social_profiles', 'notes']:
            if key in stats and isinstance(stats[key], dict):
                total_stats[key]['extracted'] += stats[key].get('extracted', 0)
                total_stats[key]['skipped'] += stats[key].get('skipped', 0)

        if 'extraction_mode' in stats:
            total_stats['extraction_modes'].append(stats['extraction_mode'])

        logger.info(
            f"Extracted from database: {db_id}",
            extra={
                "run_id": run_id,
                "extraction_id": extraction_id,
                "database_id": db_id,
                "stats": stats,
            }
        )

    # Complete extraction
    record_extraction_complete(
        bq_client, dataset_id, extraction_id, extraction_timestamp,
        total_stats, run_id
    )

    # Record completion in audit trail
    governance.record_audit(
        category="data_extraction",
        level="info",
        operation="extract_apple_contacts_raw",
        component="identity_raw_capture",
        agent="system",
        action="extraction_completed",
        success=True,
        context={
            "extraction_id": extraction_id,
            "total_stats": total_stats,
            "run_id": run_id,
        }
    )

    logger.info(
        "Apple Contacts raw extraction completed",
        extra={
            "run_id": run_id,
            "extraction_id": extraction_id,
            "total_stats": total_stats,
        }
    )

    return extraction_id

def extract_database(
    bq_client,
    dataset_id: str,
    extraction_id: str,
    extraction_timestamp: datetime,
    db_path: str,
    db_id: str,
    run_id: str
) -> Dict[str, Any]:
    """Extract from a single source database - PURE CAPTURE ONLY with deduplication.

    This function does NO parsing, NO processing, NO transformation.
    It simply reads SQLite rows and writes them to BigQuery as-is.
    Uses deduplication to skip unchanged entities.

    Uses central services for:
    - Logging: Structured logging with run_id
    - Cost tracking: Track BigQuery insert costs
    - Audit trail: Record extraction operations
    """
    conn = sqlite3.connect(db_path)

    try:
        # Get previous extraction state for deduplication
        previous_state = get_previous_extraction_state(bq_client, dataset_id, db_id)
        is_full_extraction = len(previous_state) == 0

        logger.info(
            f"Extraction mode: {'FULL' if is_full_extraction else 'INCREMENTAL'}",
            extra={
                "run_id": run_id,
                "extraction_id": extraction_id,
                "database_id": db_id,
                "previous_entities": len(previous_state),
            }
        )

        # Extract contact records with deduplication
        logger.debug(
            f"Extracting contact records from {db_id}",
            extra={"run_id": run_id, "extraction_id": extraction_id, "database_id": db_id}
        )
        contacts, contact_stats = extract_contact_records_raw(
            conn, extraction_id, extraction_timestamp, db_path, db_id, previous_state, run_id
        )
        if contacts:
            insert_contact_records(bq_client, dataset_id, contacts, run_id)

        # Extract phone numbers with deduplication
        logger.debug(
            f"Extracting phone numbers from {db_id}",
            extra={"run_id": run_id, "extraction_id": extraction_id, "database_id": db_id}
        )
        phones, phone_stats = extract_phone_numbers_raw(
            conn, extraction_id, extraction_timestamp, db_path, db_id, previous_state, run_id
        )
        if phones:
            insert_phone_numbers(bq_client, dataset_id, phones, run_id)

        # Extract email addresses with deduplication
        logger.debug(
            f"Extracting email addresses from {db_id}",
            extra={"run_id": run_id, "extraction_id": extraction_id, "database_id": db_id}
        )
        emails, email_stats = extract_email_addresses_raw(
            conn, extraction_id, extraction_timestamp, db_path, db_id, previous_state, run_id
        )
        if emails:
            insert_email_addresses(bq_client, dataset_id, emails, run_id)

        # Extract social profiles with deduplication
        logger.debug(
            f"Extracting social profiles from {db_id}",
            extra={"run_id": run_id, "extraction_id": extraction_id, "database_id": db_id}
        )
        social_profiles, social_stats = extract_social_profiles_raw(
            conn, extraction_id, extraction_timestamp, db_path, db_id, previous_state, run_id
        )
        if social_profiles:
            insert_social_profiles(bq_client, dataset_id, social_profiles, run_id)

        # Extract notes with deduplication
        logger.debug(
            f"Extracting notes from {db_id}",
            extra={"run_id": run_id, "extraction_id": extraction_id, "database_id": db_id}
        )
        notes, note_stats = extract_notes_raw(
            conn, extraction_id, extraction_timestamp, db_path, db_id, previous_state, run_id
        )
        if notes:
            insert_notes(bq_client, dataset_id, notes, run_id)

    finally:
        conn.close()

    # Return counts and stats - no validation, no processing
    return {
        'contacts': contact_stats,
        'phones': phone_stats,
        'emails': email_stats,
        'social_profiles': social_stats,
        'notes': note_stats,
        'extraction_mode': 'full' if is_full_extraction else 'incremental'
    }

def get_previous_extraction_state(
    bq_client,
    dataset_id: str,
    source_database_id: str
) -> Dict[str, Dict[str, Any]]:
    """Get previous extraction state for deduplication.

    Returns a map of apple_unique_id -> {modification_date, extraction_id}
    for all entities in the most recent extraction of this database.

    Returns empty dict if no previous extraction exists (full extraction mode).
    """
    query = f"""
    SELECT
      apple_unique_id,
      modification_date,
      extraction_id
    FROM `{bq_client.project}.{dataset_id}.raw_apple_contacts_records`
    WHERE source_database_id = @source_database_id
      AND extraction_id = (
        SELECT extraction_id
        FROM `{bq_client.project}.{dataset_id}.raw_apple_contacts_extractions`
        WHERE source_databases[OFFSET(0)].database_id = @source_database_id
        ORDER BY extraction_timestamp DESC
        LIMIT 1
      )
    """

    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("source_database_id", "STRING", source_database_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()

        state_map = {}
        for row in results:
            state_map[row['apple_unique_id']] = {
                'modification_date': row['modification_date'],
                'extraction_id': row['extraction_id']
            }

        return state_map
    except Exception as e:
        # No previous extraction - return empty (full extraction mode)
        logger.info(
            f"No previous extraction found for {source_database_id} - full extraction mode",
            extra={"source_database_id": source_database_id, "error": str(e)}
        )
        return {}

def extract_contact_records_raw(
    conn: sqlite3.Connection,
    extraction_id: str,
    extraction_timestamp: datetime,
    db_path: str,
    db_id: str,
    previous_state: Dict[str, Dict[str, Any]],
    run_id: str
) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Extract contact records with deduplication.

    Reads rows from ZABCDRECORD table and returns only new/modified records.
    PURE CAPTURE ONLY - no transformation, no interpretation.

    Args:
        conn: SQLite connection
        extraction_id: Current extraction ID
        extraction_timestamp: Extraction timestamp
        db_path: Source database path
        db_id: Source database ID
        previous_state: Map of apple_unique_id -> modification_date from previous extraction
        run_id: Run ID for logging

    Returns:
        Tuple of (records to extract, stats dict with extracted/skipped counts)
    """
    cursor = conn.cursor()

    # Get all column names
    cursor.execute("PRAGMA table_info(ZABCDRECORD)")
    columns = [row[1] for row in cursor.fetchall()]

    # Read ALL records - no WHERE clause, no filtering
    cursor.execute("SELECT * FROM ZABCDRECORD")

    records = []
    stats = {'extracted': 0, 'skipped': 0}

    for row in cursor.fetchall():
        # Convert row to dict with all columns
        record = dict(zip(columns, row))

        # Get apple_unique_id and modification_date for deduplication
        apple_unique_id = record.get('ZUNIQUEID')
        modification_date = record.get('ZMODIFICATIONDATE')

        # Deduplication check
        if apple_unique_id and apple_unique_id in previous_state:
            previous_mod_date = previous_state[apple_unique_id]['modification_date']

            # Skip if modification_date hasn't changed
            if modification_date == previous_mod_date:
                stats['skipped'] += 1
                continue  # Skip unchanged record

        # Record is new or modified - extract it
        stats['extracted'] += 1

        # Add extraction metadata (only metadata, no data transformation)
        record['extraction_id'] = extraction_id
        record['extraction_timestamp'] = extraction_timestamp
        record['source_file_path'] = db_path
        record['source_database_id'] = db_id

        # Store complete record as JSON (for reference)
        # This is the ONLY place we create JSON - it's a copy, not a transformation
        record['raw_record_json'] = json.dumps(record, default=str)

        records.append(record)

    logger.info(
        f"Extracted {stats['extracted']} contact records, skipped {stats['skipped']} unchanged",
        extra={
            "run_id": run_id,
            "extraction_id": extraction_id,
            "database_id": db_id,
            "stats": stats,
        }
    )

    return records, stats

def insert_contact_records(
    bq_client,
    dataset_id: str,
    records: List[Dict[str, Any]],
    run_id: str
) -> None:
    """Insert contact records into BigQuery - PURE WRITE ONLY.

    Uses central services for:
    - Cost tracking: Track BigQuery insert costs
    - Logging: Structured logging with run_id
    """
    if not records:
        logger.debug("No contact records to insert", extra={"run_id": run_id})
        return

    table_id = f"{bq_client.project}.{dataset_id}.raw_apple_contacts_records"

    logger.info(
        f"Inserting {len(records)} contact records to BigQuery",
        extra={
            "run_id": run_id,
            "table_id": table_id,
            "record_count": len(records),
        }
    )

    # Use BigQuery client's load_table_from_json for efficient batch insert
    # This automatically tracks costs via central services
    errors = bq_client.load_table_from_json(
        records,
        table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
    )

    if errors:
        logger.error(
            f"Errors inserting contact records",
            extra={
                "run_id": run_id,
                "table_id": table_id,
                "error_count": len(errors),
                "errors": errors[:10],  # First 10 errors
            }
        )
        raise RuntimeError(f"Failed to insert contact records: {errors[:5]}")

    # Cost tracking is automatic via BigQuery client wrapper
    # But we can explicitly track if needed
    track_cost(
        service="bigquery",
        operation="insert",
        cost=0.0,  # Cost calculated by BigQuery client
        metadata={
            "table": table_id,
            "rows_inserted": len(records),
            "run_id": run_id,
        }
    )

    logger.info(
        f"Successfully inserted {len(records)} contact records",
        extra={
            "run_id": run_id,
            "table_id": table_id,
            "record_count": len(records),
        }
    )
```

---

## Data Preservation Principles

### 1. **Pure Capture - No Transformation**
- **Store data exactly as it appears in Apple Contacts SQLite**
- **NO field mapping, NO data type conversion (beyond SQLite → BigQuery basics)**
- **NO normalization, NO formatting, NO validation**
- Preserve all fields, even if not immediately useful
- Maintain original data values exactly as stored

### 2. **No Processing or Business Logic**
- **NO filtering** (extract ALL records, not just `Z_ENT = 22`)
- **NO parsing** (store raw values, don't interpret)
- **NO validation** (don't check data quality)
- **NO relationships** (don't verify foreign keys)
- **NO categorization** (don't assign categories)
- **NO inference** (don't derive new fields)

### 3. **Complete Audit Trail**
- Track every extraction run
- Record source file paths and timestamps
- Maintain extraction metadata
- **Track what was extracted, not what it means**

### 4. **Raw JSON Preservation**
- Store complete record as JSON for reference
- Enables reprocessing if schema changes
- Supports debugging and validation
- **JSON is exact copy of SQLite row**

### 5. **Temporal Tracking**
- Track extraction timestamps
- Enable time-series analysis
- Support incremental updates
- **Track when data was captured, not when it was processed**

### 6. **Source Traceability**
- Link all records to source database
- Preserve source file paths
- Enable data lineage tracking
- **Know where data came from, not what it represents**

---

## What This Layer Does NOT Do

**CRITICAL**: The raw capture layer does NOT:

- ❌ **Parse data** - No interpretation of field values
- ❌ **Process data** - No business logic or transformations
- ❌ **Filter data** - Extract ALL records, not just contacts
- ❌ **Normalize data** - Store values exactly as they appear
- ❌ **Validate data** - No data quality checks
- ❌ **Categorize data** - No relationship or category assignment
- ❌ **Link data** - No foreign key verification or relationship building
- ❌ **Derive fields** - No computed or inferred values
- ❌ **Format data** - No reformatting or standardization

**The raw capture layer is a pure data copy operation: SQLite → BigQuery, nothing more.**

## Central Services Integration

### Required Services

The extraction script MUST use the following central services:

1. **Run Service** (`get_current_run_id()`)
   - Track extraction run with run_id
   - Include run_id in all logs and operations
   - Link extraction to pipeline run

2. **Log Service** (`get_logger(__name__)`)
   - Structured logging with run_id, extraction_id
   - Log all extraction steps
   - Log errors and warnings

3. **Cost Service** (`track_cost()`)
   - Track BigQuery insert costs
   - Track SQLite read operations (if applicable)
   - Record cost metadata

4. **ID Service** (`generate_run_id()`)
   - Generate extraction_id
   - Generate any needed identifiers

5. **BigQuery Client** (`get_bigquery_client()`)
   - Use central BigQuery client wrapper
   - Automatic cost tracking
   - Automatic retry logic

6. **Governance Service** (`get_unified_governance()`)
   - Record audit trail events
   - Track extraction operations
   - Record success/failure

7. **Pre-Run Validation** (`validate_before_run()`)
   - Validate before extraction starts
   - Check for uncommitted changes
   - Check for errors

### Service Usage Pattern

```python
# 1. Import central services
from architect_central_services import (
    get_logger,
    get_current_run_id,
    track_cost,
    get_bigquery_client,
    generate_run_id,
)
from architect_central_services.governance.governance_service.unified_governance import (
    get_unified_governance,
)
from architect_central_services.governance.pre_run_validator import validate_before_run

# 2. Initialize logger
logger = get_logger(__name__)

# 3. Pre-run validation
validate_before_run()

# 4. Get run context
run_id = get_current_run_id()

# 5. Initialize services
bq_client = get_bigquery_client(project_id=project_id)
governance = get_unified_governance()

# 6. Use in operations
logger.info("Operation", extra={"run_id": run_id, "component": "extraction"})
track_cost(service="bigquery", operation="insert", cost=0.0, metadata={"run_id": run_id})
governance.record_audit(...)
```

## Next Steps

1. ✅ **Create BigQuery Tables**: DDL already created in `identity/sql/create_raw_capture_tables.sql`
2. **Build Extraction Script**: Implement pure read/write from SQLite to BigQuery with central services
3. **Run Initial Extraction**: Extract current Apple Contacts archive
4. **Verify Counts**: Check that record counts match (no validation of content)
5. **Document Process**: Create extraction runbook

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0
**Status**: Raw Capture Design Complete
