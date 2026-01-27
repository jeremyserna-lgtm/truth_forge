# Identity Layer - Apple Contacts Source Location

**Version**: 1.0.0
**Date**: 2025-12-08
**Status**: Source Location Identified
**Owner**: Jeremy Serna

---

## macOS Contacts Database Location

### Primary Location

**Path**: `~/Library/Application Support/AddressBook/`

This is the **live, active Contacts database** on macOS. It's the source of truth for all contacts on your Mac.

### Database Structure

```
~/Library/Application Support/AddressBook/
├── AddressBook-v22.abcddb          # Main database
├── AddressBook-v22.abcddb-shm      # Shared memory file
├── AddressBook-v22.abcddb-wal      # Write-ahead log
├── ABAssistantChangelog.aclcddb     # Assistant changelog
├── Metadata/                        # Metadata files
└── Sources/                         # Source-specific databases
    ├── 01F34B8E-209B-41B0-B699-B8C2C7A00AC5/
    │   └── AddressBook-v22.abcddb  # Source 1 (534 contacts)
    ├── CD98D052-F93A-43FE-A252-28461492BF25/
    │   └── AddressBook-v22.abcddb  # Source 2 (1,116 contacts)
    └── D80C13F5-B7C3-4898-957F-E4EDEDF44966/
        └── AddressBook-v22.abcddb  # Source 3 (1 contact)
```

### Database Details

| Database | Path | Contacts | Status |
|----------|------|----------|--------|
| **Main** | `AddressBook-v22.abcddb` | 0 (container) | Active |
| **Source 1** | `Sources/01F34B8E-209B-41B0-B699-B8C2C7A00AC5/AddressBook-v22.abcddb` | 534 | Active |
| **Source 2** | `Sources/CD98D052-F93A-43FE-A252-28461492BF25/AddressBook-v22.abcddb` | 1,116 | Active |
| **Source 3** | `Sources/D80C13F5-B7C3-4898-957F-E4EDEDF44966/AddressBook-v22.abcddb` | 1 | Active |

**Total Contacts**: 1,651 contacts across all source databases

### File Details

**Main Database**:
- **Path**: `~/Library/Application Support/AddressBook/AddressBook-v22.abcddb`
- **Size**: ~1.4 MB
- **Last Modified**: 2025-11-25 01:26
- **WAL Size**: ~3.4 MB (active write-ahead log)
- **Status**: Live, actively used by Contacts app

**Source Databases**:
- Located in `Sources/{UUID}/` subdirectories
- Each source represents a sync source (iCloud, local, etc.)
- Contain the actual contact records

### Extraction Strategy

1. **Extract from Live Database**
   - Use `~/Library/Application Support/AddressBook/` as source
   - Extract from main database (if it has data)
   - Extract from all source databases in `Sources/` directory

2. **Handle WAL Files**
   - SQLite automatically uses WAL files for reads
   - No special handling needed - SQLite handles it

3. **Incremental Extraction**
   - Use `modification_date` from `ZMODIFICATIONDATE` field
   - Compare with previous extraction to skip unchanged records
   - Extract only new or modified contacts

### Default Path Configuration

The extraction script should default to:
```python
DEFAULT_CONTACTS_DB_PATH = os.path.expanduser("~/Library/Application Support/AddressBook/")
```

This ensures:
- Works out of the box on macOS
- Uses the live, active Contacts database
- No need to specify path manually
- Can be overridden if needed

### Access Considerations

1. **File Permissions**
   - Contacts database is in user's Library directory
   - Requires read access to `~/Library/Application Support/AddressBook/`
   - Standard user permissions should be sufficient

2. **Database Locking**
   - Contacts app may have database open
   - SQLite handles concurrent reads gracefully
   - WAL mode allows concurrent reads/writes
   - Extraction should work even if Contacts app is open

3. **File Changes**
   - Database is actively modified by Contacts app
   - Extraction captures state at point in time
   - Subsequent extractions will capture changes

### Backup Considerations

The archive you provided (`Contacts - 12-08-2025.abbu`) is a **backup/export**, not the live database. For ongoing extraction, we should use the **live database** at:

```
~/Library/Application Support/AddressBook/
```

This ensures:
- Always up-to-date data
- Captures changes as they happen
- No need to manually export/backup
- Supports incremental extraction

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0
**Status**: Source Location Identified and Documented
